import React, { useState, useEffect } from 'react';
import './App.css';


// The main component of our application
function App() {
  // `useState` is a React Hook that lets you add a state variable to your component.
  // `messages` will hold the array of messages fetched from the backend.
  // `setMessages` is the function we use to update the `messages` state.
  const [messages, setMessages] = useState([]);

  // `newMessage` will hold the value of the text input field.
  // `setNewMessage` is the function we use to update the `newMessage` state.
  const [newMessage, setNewMessage] = useState('');

  // State for image functionality
  const [images, setImages] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageTitle, setImageTitle] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');

  // `useEffect` is a React Hook that lets you synchronize a component with an external system.
  // In this case, we use it to fetch data from our Django backend when the component first loads.
  // The empty array `[]` as the second argument means this effect will only run once, after the initial render.
  useEffect(() => {
    // Fetch messages
    fetch('http://localhost:8000/api/messages/')
      .then(response => response.json())
      .then(data => setMessages(data));

    // Fetch images
    fetch('http://localhost:8000/api/images/')
      .then(response => response.json())
      .then(data => {
        console.log('Fetched images:', data);
        setImages(data);
      });
  }, []);

  // This function is called when the form is submitted.
  const handleSubmit = (e) => {
    // `e.preventDefault()` stops the browser from reloading the page, which is the default behavior for form submissions.
    e.preventDefault();

    // We send a POST request to our backend to create a new message.
    fetch('http://localhost:8000/api/messages/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      // We send the new message in the request body, formatted as JSON.
      body: JSON.stringify({ body: newMessage })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      setMessages([...messages, data]);
      setNewMessage('');
    })
    .catch(error => {
      console.error('There has been a problem with your fetch operation:', error);
    });
  };

  // Handle file selection
  const handleFileSelect = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  // Handle image upload
  const handleImageUpload = (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setUploadStatus('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('title', imageTitle);

    setUploadStatus('Uploading...');

    fetch('http://localhost:8000/api/images/', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Upload failed');
      }
      return response.json();
    })
    .then(data => {
      setImages([data, ...images]);
      setSelectedFile(null);
      setImageTitle('');
      setUploadStatus('Upload successful!');
      // Clear the file input
      document.getElementById('imageInput').value = '';
    })
    .catch(error => {
      console.error('Upload error:', error);
      setUploadStatus('Upload failed. Please try again.');
    });
  };

  // This is the JSX that defines the structure of our component. It looks like HTML, but it's actually JavaScript.
  return (
    <div className="App">
      <header className="App-header">
        <h1>Decoupled Django React App</h1>
      </header>
      <div className="App-content">
        <h2>Messages</h2>
        <ul>
          {/* We use the `map` function to loop over the `messages` array and create a list item for each message. */}
          {/* The `key` attribute is important for React to keep track of each item in the list. */}
          {messages.map(message => (
            <li key={message.id}>{message.body}</li>
          ))}
        </ul>
        {/* When this form is submitted, it will call the `handleSubmit` function. */}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            // The `value` of the input is tied to the `newMessage` state.
            value={newMessage}
            // `onChange` is called every time the user types in the input field.
            // We update the `newMessage` state with the new value.
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Enter a new message"
          />
          <button type="submit">Send</button>
        </form>

        {/* Image Upload Section */}
        <div className="image-section">
          <h2>Upload Images</h2>
          <form onSubmit={handleImageUpload}>
            <div>
              <input
                type="text"
                value={imageTitle}
                onChange={(e) => setImageTitle(e.target.value)}
                placeholder="Enter image title (optional)"
              />
            </div>
            <div>
              <input
                id="imageInput"
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
              />
            </div>
            <button type="submit">Upload Image</button>
          </form>
          {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
        </div>

        {/* Image Gallery */}
        <div className="image-gallery">
          <h2>Image Gallery</h2>
          <div className="images-grid">
            {images.map(image => (
              <div key={image.id} className="image-item">
                <img
                  src={image.image_url}
                  alt={image.title || 'Uploaded image'}
                  onError={(e) => {
                    console.error('Image failed to load:', image.image_url);
                    e.target.style.backgroundColor = '#f0f0f0';
                    e.target.style.color = '#666';
                    e.target.alt = 'Image not available';
                  }}
                />
                {image.title && <p className="image-title">{image.title}</p>}
                <p className="image-date">
                  Uploaded: {new Date(image.uploaded_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// We export the `App` component so it can be used in other parts of our application (specifically, `src/index.js`).
export default App;
