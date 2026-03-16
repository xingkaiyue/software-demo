from src.GraphBase.graph.graphDataBase import GraphDatabase

class GraphHandler:
    def __init__(self):
        self.db = GraphDatabase()

    # def create_graph(self, data):
    #     if not self.db.is_running():
    #         print("Neo4j 连接失败，请检查配置和服务是否正常。")
    #         exit(1)
    #
    #     print(" 已连接 Neo4j")
    #
    #     self.db.delete_entities()
    #     print(" 已删除所有节点和关系")
    #
    #     # 读取 jsonl
    #     # triples = self.db.load_jsonl(path)
    #     triples = self.db.load_triples(data)
    #
    #     # 写入数据库
    #     self.db.add_triples(triples)
    #     print(f"成功写入 {len(triples)} 条三元组")
    #
    #     # 查询统计
    #     info = self.db.get_graph_info()
    #     print(f"当前图数据库状态: {info}")

    def create_graph(self, data):
        if not self.db.is_running():
            print("Neo4j 连接失败，请检查配置和服务是否正常。")
            exit(1)

        print(" 已连接 Neo4j")

        self.db.delete_entities()
        print(" 已删除所有节点和关系")

        # 读取数据 - 直接传入文件路径
        triples = self.db.load_triples(data)  # 这里会调用修改后的方法

        if not triples:
            print(" 没有有效数据可导入")
            return

        # 写入数据库
        self.db.add_triples(triples)
        print(f" 成功写入 {len(triples)} 条三元组")

        # 查询统计
        info = self.db.get_graph_info()
        print(f" 当前图数据库状态: {info}")

    def serialize_neo4j_data(self, data):
        """
        将 Neo4j 图数据序列化为 JSON 格式
        """
        nodes = []
        edges = []
        node_ids = set()

        for item in data:
            if len(item) == 3:
                node1, relationship, node2 = item

                # 处理节点1
                if node1._element_id not in node_ids:
                    nodes.append({
                        'id': node1._element_id,
                        'name': node1._properties.get('name', ''),
                    })
                    node_ids.add(node1._element_id)

                # 处理节点2
                if node2._element_id not in node_ids:
                    nodes.append({
                        'id': node2._element_id,
                        'name': node2._properties.get('name', ''),
                    })
                    node_ids.add(node2._element_id)

                # 处理关系
                edges.append({
                    'source': node1._element_id,
                    'target': node2._element_id,
                    'relation': relationship.type,
                })

        return {
            'nodes': nodes,
            'edges': edges
        }

    def get_graph(self):
        if not self.db.is_running():
            print("Neo4j 连接失败，请检查配置和服务是否正常。")
            exit(1)

        print("已连接 Neo4j")

        json_data = self.serialize_neo4j_data(self.db.get_sample_nodes())

        return json_data

    def close_graph(self):
        self.db.close()
        print("关闭连接")

if __name__ == "__main__":
    jsonl_path = r"../../data/graph/kg_前端_expanded.jsonl"

    graph = GraphHandler()
    graph.create_graph(jsonl_path)
    print(graph.get_graph())
    graph.close_graph()
