import React, { useState, useRef, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
  import axios from 'axios'; // Make sure to import axios if you use it
  import styled from 'styled-components';
import { Navbar, Nav, Form, Button, Container, FormControl } from 'react-bootstrap';


function RegistrationForm() {
  const [name, setName] = useState('');
  const [id, setId] = useState('');
  const [department, setDepartment] = useState('');
  const [time, setTime] = useState('');   
  const [imageData, setImageData] = useState('');                  

  const handleSubmit = (e) => {
    e.preventDefault();

    // Capture the image when the form is submitted
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    context.drawImage(videoRef.current, 0, 0, 640, 480);
    const capturedImageData = canvas.toDataURL('image/png');
    
    // Set the captured image data in the state
    setImageData(capturedImageData);

    // Prepare the data to send to the server (name, id, department, time, and imageData)
    const formData = {
      name,
      id,
      department,
      time,
      image: capturedImageData,
    };

    // Send the formData to the server
    axios.post('http://localhost:5000/new-employee', formData)
      .then((response) => {
        // Handle the server response here
        console.log(response.data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

//   function App() {
 
    const [statusMessage, setStatusMessage] = useState('');
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const postData = async (url, data) => {
      try {
        const response = await axios.post(url, data, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
    
        // Check if the response has a data property
        if (response.data) {
          setStatusMessage(response.data);
        } else {
          setStatusMessage('Received an empty response from the server.');
        }
      } catch (error) {
        setStatusMessage("Error performing operation.");
        console.error("Error:", error);
      }
    };
    
    useEffect(() => {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          navigator.mediaDevices.getUserMedia({ video: true }).then(function (stream) {
            const video = videoRef.current;
            video.srcObject = stream;
            const playPromise = video.play();
        
            if (playPromise !== undefined) {
                playPromise.then(_ => {
                    // Automatic playback started!
                }).catch(error => {
                    console.error("Playback failed: ", error);
                });
            }
        });
        
        }
      }, []);
const handleClick = () => {
            const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    context.drawImage(videoRef.current, 0, 0, 640, 480);

    const capturedImageData = canvas.toDataURL('image/png');
    setImageData(capturedImageData); // Store the captured image data
  };
  const clearForm = (e) => {
    e.preventDefault(); // prevent default behavior
    setName('');
    setId('');
    setDepartment('');
    setTime('');
    setImageData(''); // adjusted the state name from 'image' to 'imageData' as you used above
  };
  return (
    <Container>
    <div>
      <h2>Registration Form</h2>
      <form onSubmit={handleSubmit} id="myForm">
        <div className="form-group">
          <label>Name</label>
          <input
            type="text"
            className="form-control"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>ID</label>
          <input
            type="text"
            className="form-control"
            value={id}
            onChange={(e) => setId(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Department</label>
          <input
            type="text"
            className="form-control"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            required
          />
        </div>
          <div className="camera-container">
            <video ref={videoRef} width="640" height="480" autoplay></video>
            {/* <Button className="btn btn-primary mt-3" onClick={handleClick}>Snap Photo</Button> */}
            {/* ... Other buttons ... */}
            {imageData && (
                <canvas ref={canvasRef} width="640" height="480" className="mt-3"></canvas>
            //   <img src={imageData} alt="Captured" width="200" height="150" />
            )}
            <canvas ref={canvasRef} width="640" height="480" className="mt-3"></canvas>
            <p className="mt-3 text-center">{statusMessage}</p>
          </div>
        <button type="submit" className="btn btn-primary">
          Register
        </button>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <button type="submit"  onClick={clearForm} className="btn btn-primary">
          Clear
        </button>
      </form>
    </div>
    
</Container>


  );
}
//}

export default RegistrationForm;