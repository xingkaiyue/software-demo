# 关系 → (头实体类型, 尾实体类型)
RELATION_TYPE_MAP = {
    "常见症状": ("疾病", "症状"),
    "所属科室": ("疾病", "科室"),
    "治疗方式": ("疾病", "治疗方式"),
    "并发症": ("疾病", "疾病"),
    "禁忌": ("疾病", "行为"),
    "高发人群": ("疾病", "人群"),
    "检查方式": ("疾病", "检查方式"),
    "常用药物": ("疾病", "药物"),
    "预防方式": ("疾病", "预防方式"),
    "风险因素": ("疾病", "风险因素"),
    "护理要点": ("疾病", "护理要点"),
    "传播方式": ("疾病", "传播方式"),
    "致病原因": ("疾病", "病因"),
    "危害": ("疾病", "危害"),
    "严重程度": ("疾病", "程度"),
    "紧急处理": ("疾病", "处理方式"),
    "病程时长": ("疾病", "时长"),
    "康复周期": ("疾病", "时长"),
    "改善方式": ("疾病", "改善方式"),
    "诱因": ("疾病", "诱因"),
    "诱发因素": ("疾病", "诱因"),
    "类型": ("疾病", "类型"),
    "特点": ("事物", "特点"),
    "好处": ("事物", "好处"),
    "适用疾病": ("药物", "疾病"),
    "适用症状": ("药物", "症状"),
    "适用人群": ("事物", "人群"),
    "药品类型": ("药物", "类型"),
    "功效": ("药物", "功效"),
    "禁忌人群": ("药物", "人群"),
    "用法": ("药物", "用法"),
    "注意事项": ("药物", "注意事项"),
    "检查项目": ("检查方式", "检查项目"),
    "适用场景": ("检查方式", "场景"),
    "适用部位": ("检查方式", "部位"),
    "等级": ("医院", "等级"),
    "功能": ("事物", "功能"),
    "用途": ("事物", "用途"),
    "作用": ("事物", "作用"),
    "食物来源": ("营养素", "食物"),
    "来源": ("事物", "来源"),
    "适合人群": ("事物", "人群"),
    "核心": ("事物", "核心"),
    "重要性": ("事物", "重要性"),
    "维护方式": ("事物", "方式"),
    "特点": ("事物", "特点"),
    "好处": ("事物", "好处"),
    "危害": ("行为", "危害"),
    "建议量": ("事物", "数量"),
    "建议频率": ("事物", "频率"),
    "方法": ("事物", "方法"),
    "适用情况": ("事物", "情况"),
    "紧急程度": ("疾病", "程度"),
    "诊疗范围": ("科室", "疾病"),
    "擅长": ("医院", "能力"),
    "服务": ("医院", "服务"),
    "项目": ("体检中心", "项目"),
    "必查项目": ("体检", "项目"),
    "最佳时间": ("疫苗", "时间"),
    "接种季节": ("疫苗", "季节"),
    "核心原则": ("急救", "原则"),
}

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
        """添加三元组到图谱（支持不同节点类型）"""

        def create(tx, triples):
            for triple in triples:
                # ① 根据关系推断实体类型
                h_type, t_type = RELATION_TYPE_MAP.get(
                    triple["r"],
                    ("Entity", "Entity")  # 兜底策略
                )

                # ② 用不同 Label 创建节点
                tx.run(
                    f"""
                    MERGE (h:{h_type} {{name: $h}})
                    MERGE (t:{t_type} {{name: $t}})
                    MERGE (h)-[r:`{triple['r']}`]->(t)
                    """,
                    h=triple["h"],
                    t=triple["t"]
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
