Installation guide : 

Prerequisites to be installed on the system before deploying the app:
1) python3.8 including pip for python3+
2) git
3) docker
4) nodejs with npm utility

Deployment Steps
1) Get the code from git
Execute command : git clone https://github.com/pradeeptyagi23/GraphQL-Test.git

2) Get the dataset from the url
	chmod +x get_data.sh
	./get_data.sh
	This will get the the zip file from the url and extract it in the folder named dataset/ under the backend/ folder

3) Run redisgraph docker container
Execute command  "docker run -d -p 6379:6379 -it --rm redislabs/redisgraph"
This will start redisgraph on the localhost port 6379 which will be used by the backend server for connection purposes.

4) Build and Run fastAPI backend server
	cd backend

	Execute command : pip install -r requirements.txt
	This will install all the required python dependencies on the system.

	Execute command: uvicorn app.backend_server:app --reload --host 127.0.0.1
	This will start the backend server on port 8000 on localhost via uvicorn service (This service is an orchestrator to run asgi apps like fastapi) 


5) Build and Run the react app.
	cd frontend
	Execute command : npm init
	This will install all react dependencies from the package.json
	
	Execute command: npm start
	This will start the frontend on port 3000 on the localhost
	

6) Access UI
	Got to url http://localhost:3000 . 
	Click button load graph data. 
	This will load the graph data from the dataset/ folder and create relationship based on the edges in the dataset.
	Select any relationship from the dropdown to view the graph.


Solution Description:
1) Data load
	This solution uses redisgraph as the datastore for storing the graph data from the dataset.
	On Clicking of "LOAD GRAPH DATA" button on the UI . The backend server will execute following steps in order to store the data and its relationship.
	*** A maximum of 100 entries for each link type is extracted. 
	a) Get references to the nodes from the edge file within the dataset. This will create a map of the entity and its related nodes including the link between them like
	[<entity_node_id> = {'related_node':<related_node_id>,'link':<link_between_nodes>,'type':'type_of_link']
	b) Add the node_ids and its related node node_ids to to list. 
	c) As we are considering only a subset of data, the nodes file will be accessed for only the node_ids that
	are present within the node_ids list created in step b.
	d) Create a Node in redisgraph for each node_id within the list created in the step b.
	e) Create relationships for each node created in step d using the related_nodes map created in step A.
	
	Example cypher query that is executed is as follows:
	query = """MATCH (x:entity {node_id: $start_id}),(c:address {node_id:$end_id}) CREATE (x)-[:"""+relation+"""]->(c)"""
	where start_id : Is the id of the label entity that corresponds to a specfic node.
	$end_id : Is the node_id of the node denoting address of the entity in this case.
	relation : Is the registered address in this case

2) Get data on the frontend.
	On selecting a link from the dropdown on the UI. The following steps are executed:
	a) The UI sends a request to the backend with the link name selected from the UI
	b) The backend with get the start node details, the link details and the end node details via query to the redisgraph.

	Example cypher query is as follows:
	query = "MATCH (i)-[s:"+relation+"]->(c) RETURN i.node_id,i.name,c.node_id,c.name"
	where relation : Is the the link name selected on the UI

	c) The backend will then return data in the form of {"nodes":[],"links":[]} , that contains the nodes and their links reference the nodes as "source" and "target"
	d) The UI uses react-force-graph of the type 2d text node to render the data returned via the backend 


Backlog:
Following are the gaps I see and how this solution can be improved.
1) We can use more production ready datastore for storing graph data like neo4j
2) Data mutations can be handled on the frontend via state management, so any realtime data updates to the graph dataset can be quickly rendered on the frontend.
3) Full capabilitied of fastapi can be acheived by using the asynchronous functionality to load and getData.

