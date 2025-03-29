import { useState } from "react";
import FileUploadBox from "../components/FileUploadBox";

function WeightDataPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }
  
    setLoading(true);
    setError(null);
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      console.log("Sending request to server...");
      const response = await fetch("http://localhost:5000/weight", {
        method: "POST",
        body: formData,
      });
  
      console.log("Response received:", response.status);
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      const data = await response.text(); // Expect plain text response
      console.log("Data received:", data);
  
      setResult(data); // Store text response directly
    } catch (error) {
      console.error("Error:", error);
      setError("Failed to fetch insights. Please make sure the server is running.");
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <div className="min-h-screen w-screen bg-gradient-to-b from-white to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-white rounded-2xl shadow-xl p-8 text-center mx-4">
        <h1 className="text-3xl sm:text-4xl font-semibold text-gray-800 mb-4">
          Track Your Weight Data
        </h1>
        <p className="text-gray-500 mb-6 text-base sm:text-lg">
          Measure your progress and predict your weight loss journey.
        </p>

        <FileUploadBox
          accept=".csv,.xlsx"
          onFileSelect={handleFileSelect}
          labelText="Drag & drop CSV file here or click to choose"
        />

        <button
          onClick={handleUpload}
          className="mt-4 w-full bg-white text-black px-6 py-3 rounded-full hover:bg-gray-100 transition duration-200"
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze Weight Data"}
        </button>

        {error && (
          <div className="mt-6 text-left text-red-500">
            {error}
          </div>
        )}

    {result && (
      <div className="mt-6 text-left">
        <h2 className="text-xl font-semibold mb-2">Weight Analysis:</h2>
        <pre className="bg-gray-100 p-4 rounded-lg text-sm text-gray-800 overflow-x-auto">
          {result}
        </pre>
      </div>
    )}


      </div>
    </div>
  );
}

export default WeightDataPage;
