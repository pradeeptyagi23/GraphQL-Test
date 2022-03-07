import './App.css';
import {useState} from 'react';
import {ForceGraph3D} from 'react-force-graph';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import SpriteText from 'three-spritetext';

function App() {

  const [relation,setRelation] = useState('')
  const [graphdata,setGraphData] = useState({"nodes":[],"links":[]})
  const [loadingData,setLoadingData] = useState(false)
 
  console.log(Object.keys(graphdata).length)

  const handleSelectRelation = async (event) => {
    setRelation(event.target.value);
    const url = 'http://localhost:8000/getData/'+event.target.value
    try {
      const response = await fetch(url);
      const json = await response.json();
      console.log(json);
      setGraphData(json)
  } catch (error) {
      console.log("error", error);
  }
  };
  const loadGraphData = async () => {
    console.log('button clicked....')
    const url = 'http://localhost:8000/loadData/'
    try {
      setLoadingData(true)
      const response = await fetch(url);
      const json = await response.json();
      console.log(json);
      if(json['status'] === 'success'){
        setLoadingData(false)
      }
  } catch (error) {
      console.log("error", error);
  }
  }
  const renderLoadButton = (
      <Button disabled={loadingData} onClick={loadGraphData} style={{'right':'100px'}} variant="contained">Load Graph Data</Button>
  )

  const renderSelectRelation = (
    <Box sx={{ minWidth: 120 }}>
    <FormControl fullWidth>
      <InputLabel id="demo-simple-select-label">Age</InputLabel>
      <Select
        labelId="demo-simple-select-label"
        id="demo-simple-select"
        value={relation}
        onChange={handleSelectRelation}
        label="Select Relationship"
      >
        <MenuItem value={'registered_address'}>registered address</MenuItem>
        <MenuItem value={'connected_to'}>connected to</MenuItem>
        <MenuItem value={'same_name_as'}>same name as</MenuItem>
        <MenuItem value={'registrar_and_transfer_agent_of'}>registrar and transfer agent of</MenuItem>
      </Select>
    </FormControl>
  </Box>
  )
  return (
    <div className="App">
      <br />
      <div style={{display:'inline-block',padding:'10px'}}>
        {renderLoadButton}
      </div>
      <div style={{display:'inline-block',padding:'10px'}}>
        {renderSelectRelation}
      </div>     
      <br />
      <br />
      <ForceGraph3D
          graphData={graphdata}
          nodeAutoColorBy="group"
          nodeThreeObject={node => {
          const sprite = new SpriteText(node.id);
          sprite.color = node.color;
          sprite.textHeight = 8;
          return sprite;
          }}
        />,
    </div>
  );
}

export default App;
