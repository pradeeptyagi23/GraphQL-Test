from importlib.resources import path
import redis,csv,os,re,sys,json
from redisgraph import Node, Edge, Graph
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
datafilepath  = 'dataset/'
os.chdir(datafilepath)
# redisurl = os.environ['REDISURL']
# print('Got url ' + redisurl)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

r = redis.Redis(host='localhost', port=6379)
redis_graph = Graph('paradise_papers', r)


'''
Get data based on the relation specified in the relation query parameter.
'''

@app.get('/getData/{relation}')
async def getData(request:Request,relation:str):
    # query = "MATCH (i)-[s:legal_representative]->(c) RETURN i.node_id,i.name,c.node_id,c.name"
    query = "MATCH (i)-[s:"+relation+"]->(c) RETURN i.node_id,i.name,c.node_id,c.name"
    result = redis_graph.query(query)
    nodes = []
    links = []
    ret_data = {}
    for record in result.result_set:
        nodes.append({'id':record[0],'node_id':record[0],'name':record[1]})
        nodes.append({'id':record[2],'node_id':record[2],'name':record[3]})
        links.append({'source':record[0],'target':record[2]})
    ret_data['nodes'] =nodes
    ret_data['links'] =links 
    return(JSONResponse(ret_data))

'''
Get related nodes including the links between them and add the nodes to node_ids list
Create a Node in the redisgraph for each node mentioned in the node_ids list.
Create relationship between nodes based on the data in the related_nodes map.
'''

@app.get('/loadData/')
async def loadData():
    related_nodes = {}
    node_ids = []
    for relationship in ['registered_address','officer_of','intermediary_of','connected_to','same_name_as']:
        for file in os.listdir():
            if 'edges' in file:
                with open(file) as edgefile:
                    edgefilereader = csv.reader(edgefile,delimiter=',')
                    line_count = 0
                    for row in edgefilereader:
                        if(line_count <100 ):
                            if row[1] == relationship:
                                line_count+=1
                                node_ids.append(row[0])
                                node_ids.append(row[2])
                                if(relationship != 'registered_address'):
                                    if(row[2] not in related_nodes):
                                        related_nodes[row[2]] = [{'related_node':row[0],'link':row[3],'type':row[1]}]
                                    else:
                                        related_nodes[row[2]].append({'related_node':row[0],'link':row[3],'type':row[1]})
                                else:
                                    if(row[0] not in related_nodes):
                                        related_nodes[row[0]] = [{'related_node':row[2],'link':row[3],'type':row[1]}]
                                    else:
                                        related_nodes[row[0]].append({'related_node':row[2],'link':row[3],'type':row[1]})

    for file in os.listdir():
        if 'nodes' in file:
            graph_label  = file.split('.')[-2]
            with open(file) as datafile:          
                csv_reader = csv.reader(datafile,delimiter=',')
                line_count = 0
                columns = {}
                for row in csv_reader:
                    line_count+=1
                    if line_count == 1:
                        columns = {i:row[i] for i in range(len(row))}                           
                    else:
                        if(row[0] in node_ids ):
                            properties = {columns[i]:row[i] for i in range(len(row))}
                            record = Node(label=graph_label,properties = properties)
                            redis_graph.add_node(record)
    else:
        print(f"Commiting data to redis")
        redis_graph.commit()


    for node,attrs in related_nodes.items():
        for attr in attrs:
            params = {'start_id':node,'end_id':attr['related_node'],'link':attr['link']}
            relation = params['link'].replace(" ","_")
            relation = relation.replace("-","_")
            query = ""
            if(attr['type'] == 'registered_address'):
                query = """MATCH (x:entity {node_id: $start_id}),(c:address {node_id:$end_id}) CREATE (x)-[:"""+relation+"""]->(c)"""
            
            elif(attr['type'] == 'connected_to'):
                query = """MATCH (x:entity {node_id: $start_id}),(c:other {node_id:$end_id}) CREATE (x)-[:"""+relation+"""]->(c)"""
            
            elif(attr['type'] == 'same_name_as'):
                query = """MATCH (x:entity {node_id: $start_id}),(c:entity {node_id:$end_id}) CREATE (x)-[:"""+relation+"""]->(c)"""

            elif(attr['type'] == 'officer_of'):
                query = """MATCH (x:entity {node_id: $start_id}),(c:officer {node_id:$end_id}) CREATE (x)-[:"""+relation+"""]->(c)"""

            elif(attr['type'] == 'intermediary_of'):
                query = """MATCH (x:entity {node_id: $start_id}),(c:intermediary {node_id:$end_id}) CREATE (x)-[:"""+relation+"""]->(c)"""
            
            if(query):
                redis_graph.query(query, params, timeout=10)
    
    return(JSONResponse({'status':'success'}))