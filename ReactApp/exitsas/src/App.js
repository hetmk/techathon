import RegistrationForm from './registration';
import ReactDOM from 'react-dom/client';
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import styled, { keyframes } from 'styled-components';
import { Navbar, Nav, Form, Button, Container, FormControl, Row, Col } from 'react-bootstrap';

// Keyframes for animations
const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const AppStyles = styled.div`
  body {
    height: 100vh;
    background: linear-gradient(45deg, #3B3B3B, #6B6B6B, #9B9B9B);
    font-family: 'Arial', sans-serif;
  }

  nav {
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
    background-color: #3B3B3B;
  }

  .navbar-brand img {
    transition: transform 0.3s;
    &:hover {
      transform: scale(1.1);
    }
  }

  .camera-container {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px;
    animation: ${fadeIn} 1s;
  }

  .response-container {
    margin-top: 20px;
    padding: 10px;
    border-radius: 10px;
    background-color: #FFF3E0;
    animation: ${fadeIn} 1s;
  }
`;

function App() {
  // ... Rest of your hooks and functions ...

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
        setStatusMessage(JSON.stringify(response.data));
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
const handleSnapClick = () => {
          // window.location.url('http://localhost:3000/registration')
          console.log("Register Now button clicked.");
          const root = ReactDOM.createRoot(document.getElementById('root'));  
          root.render(
            <React.StrictMode>
              <RegistrationForm/>
            </React.StrictMode>
            
          );
  };
const handleClick = () => {
  const canvas = canvasRef.current;
  const context = canvas.getContext('2d');
  context.drawImage(videoRef.current, 0, 0, 640, 480);

  let imageData = canvas.toDataURL('image/png');

    // Remove data URL prefix to only send base64 encoded data
    const base64Image = imageData.split(',')[1];
    
    postData('http://localhost:5000/run-face-check', {
      image: base64Image,status:'exit',
    })
    .then(response => {
        console.log('Success:', response);
    })
    .catch(error => {
        console.error('Error:', error);
    });
};

  return (
    <AppStyles>
      <Navbar bg="dark" expand="lg" variant="dark">
        <Navbar.Brand href="#">
          <img src="download.jpg" alt="Company Logo" height="50" />
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="mr-auto">
            {/* Add other Navbar items if needed */}
          </Nav>
        </Navbar.Collapse>
      </Navbar>

      <Container className="mt-4">
        <Row>
          <Col xs={12} md={6}>
            <div className="camera-container">
              <video ref={videoRef} width="320" height="240" autoPlay></video>
              <Button className="btn btn-primary mt-3" onClick={handleClick}>Exit</Button>
              <canvas ref={canvasRef} width="640" height="480" className="mt-3"></canvas>
            </div>
          </Col>
          <Col xs={12} md={6}>
            <div className="response-container">
              <h4>Server Response</h4>
              <p>{statusMessage}</p>
            </div>
          </Col>
        </Row>
        <Row className="mt-4">
          <Col xs={12}>
            <h3>New employee?<Button variant="outline-primary" className="ml-3" onClick={handleSnapClick}>Register Now</Button></h3>
          </Col>
        </Row>
      </Container>
    </AppStyles>
  );
}

export default App;
