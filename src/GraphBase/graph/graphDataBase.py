import os
import json
import warnings
from datetime import datetime
from neo4j import GraphDatabase as GD
from .config_logging.config_logging import logger
from .config import config

warnings.filterwarnings("ignore", category=UserWarning)


class GraphDatabase:
    def __init__(self):
        self.kgdb_name = "neo4j"
        self.status = "closed"
        self.driver = None
        self.embed_model_name = None
        self.work_dir = os.path.join(config.save_dir, "knowledge_graph", self.kgdb_name)
        os.makedirs(self.work_dir, exist_ok=True)

        self.load_graph_info() or logger.info("未找到已保存的图数据库信息，将创建新配置")
        self.start()

    def start(self):
        # if not (config.enable_knowledge_graph and config.enable_knowledge_base):
        #     return
        try:
            HOST = os.getenv('NEO4J_HOST')
            PORT = os.getenv('NEO4J_PORT')
            USERNAME = os.getenv('NEO4J_USERNAME')
            PASSWORD = os.getenv('NEO4J_PASSWORD')

            self.driver = GD.driver(
                f"neo4j://{HOST}:{PORT}",
                auth=(USERNAME, PASSWORD)
            )

            with self.driver.session(database=self.kgdb_name) as session:
                result = session.run("RETURN 'Hello, Neo4j!'")
                print(result.single())

            self.status = "open"
            config.enable_knowledge_graph = True
            config.enable_knowledge_base = True
            logger.info(f"Neo4j connected: {self.get_graph_info()}")
            self.save_graph_info()
        except Exception as e:
            logger.error(f"Neo4j连接失败: {e}")
            config.enable_knowledge_graph = False

    def close(self):
        if self.driver:
            self.driver.close()
            self.status = "closed"

    def is_running(self):
        return config.enable_knowledge_graph and config.enable_knowledge_base and self.status == "open"

    def use_database(self):
        if self.status == "closed": self.start()

    def _with_session(self, fn, *args, **kwargs):
        self.use_database()
        with self.driver.session() as session:
            return fn(session, *args, **kwargs)

    def save_graph_info(self):
        info = self.get_graph_info()
        if info:
            path = os.path.join(self.work_dir, "graph_info.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)

    def load_graph_info(self):
        path = os.path.join(self.work_dir, "graph_info.json")
        if os.path.exists(path):
            info = json.load(open(path, 'r', encoding='utf-8'))
            self.embed_model_name = info.get("embed_model_name")
            logger.info(f"加载图数据库信息: {info.get('last_updated')}")
            return True
        return False

    def get_graph_info(self):
        def query(tx):
            ec = tx.run("MATCH (n) RETURN count(n) AS count").single()["count"]
            rc = tx.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
            labels = tx.run("CALL db.labels() YIELD label RETURN collect(label) AS labels").single()["labels"]
            return {
                "graph_name": self.kgdb_name,
                "entity_count": ec,
                "relationship_count": rc,
                "labels": labels,
                "status": self.status,
                "embed_model_name": self.embed_model_name,
                "last_updated": datetime.now().isoformat()
            }
        return self._with_session(lambda s: s.execute_read(query))

    def get_sample_nodes(self, num=50):
        def query(tx, num):
            return tx.run("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT $num", num=num).values()
        return self._with_session(lambda s: s.execute_read(query, num))

    def delete_entities(self, name=None):
        def delete(tx, name):
            q = "MATCH (n" + (f" {{name: $name}}" if name else "") + ") DETACH DELETE n"
            tx.run(q, name=name)
        return self._with_session(lambda s: s.execute_write(delete, name))

    # def add_triples(self, triples):
    #     def create(tx, triples):
    #         for t in triples:
    #             tx.run(
    #                 "MERGE (a:Entity {name: $h}) MERGE (b:Entity {name: $t}) MERGE (a)-[:"+t['r']+"]->(b)",
    #                 h=t['h'], t=t['t'])
    #     return self._with_session(lambda s: s.execute_write(create, triples))
    def add_triples(self, triples):
        """添加三元组到图谱"""

        def create(tx, triples_list):
            for triple in triples_list:
                # 确保每个triple都有必要的字段
                if not all(k in triple for k in ['h', 'r', 't']):
                    print(f"⚠️ 跳过无效数据: {triple}")
                    continue

                # 执行Cypher查询
                tx.run(
                    """
                    MERGE (a:Entity {name: $head})
                    MERGE (b:Entity {name: $tail})
                    MERGE (a)-[:`{relation}`]->(b)
                    """.format(relation=triple['r']),
                    head=triple['h'],
                    tail=triple['t']
                )

        return self._with_session(lambda s: s.execute_write(create, triples))

    def query_entity(self, entity_name, hops=2, limit=100):
        def query(tx, name, hops, limit):
            q = f"MATCH (n {{name: $name}})-[r*1..{hops}]-(m) RETURN n, r, m LIMIT $limit"
            return tx.run(q, name=name, limit=limit).values()
        return self._with_session(lambda s: s.execute_read(query, entity_name, hops, limit))

    def format_to_graph(self, query_results):
        nodes, edges, node_ids = [], [], set()
        for n, rels, m in query_results:
            for rel in rels:
                s_id, t_id = n.element_id, m.element_id
                if s_id not in node_ids:
                    nodes.append({"id": s_id, "name": n["_properties"].get("name")})
                    node_ids.add(s_id)
                if t_id not in node_ids:
                    nodes.append({"id": t_id, "name": m["_properties"].get("name")})
                    node_ids.add(t_id)
                edges.append({
                    "id": rel.element_id,
                    "type": rel.type,
                    "source_id": s_id,
                    "target_id": t_id,
                })
        return {"nodes": nodes, "edges": edges}

    def load_jsonl(self, filepath):
        triples = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                triples.append(json.loads(line.strip()))
        return triples

    # def load_triples(self, data):
    #     triples = []
    #     for item in data:
    #         triples.append(item)
    #     return triples

    def load_triples(self, data):
        """加载三元组数据"""
        triples = []

        # 如果传入的是字符串（文件路径）
        if isinstance(data, str):
            # 应该是读取文件，而不是直接处理字符串
            if data.endswith('.jsonl'):
                with open(data, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                triples.append(json.loads(line))
                            except:
                                print(f" 解析失败: {line[:50]}...")
            elif data.endswith('.json'):
                with open(data, 'r', encoding='utf-8') as f:
                    triples = json.load(f)
            else:
                print(f" 不支持的文件格式: {data}")

        # 如果传入的是列表（直接传数据）
        elif isinstance(data, list):
            triples = data

        return triples


    def get_node_info(self, node_name):
        """查询单个节点的名称和ID"""

        def query(tx, name):
            result = tx.run("MATCH (n {name: $name}) RETURN n", name=name)
            record = result.single()
            if record:
                node = record["n"]
                return {
                    "id": node.element_id,
                    "name": node["name"]
                }
            return None

        return self._with_session(lambda s: s.execute_read(query, node_name))
    # 可按需增加 async 版本和 embedding 逻辑
