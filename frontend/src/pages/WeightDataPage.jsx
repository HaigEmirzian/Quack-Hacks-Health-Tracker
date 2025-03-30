import { useState, useEffect, useRef } from "react"; // Added useEffect and useRef
import FileUploadBox from "../components/FileUploadBox";
import WeightChart from "../components/WeightChart";
import RingLoader from "react-spinners/RingLoader";

function WeightDataPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const chartRef = useRef(null); // Create a ref for the chart container

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
      console.log("Sending request to http://localhost:5000/weight");
      const response = await fetch("http://localhost:5000/weight", {
        method: "POST",
        body: formData,
        timeout: 60000,
      });

      console.log("Response status:", response.status);  
      if (!response.ok) {
        const errorText = await response.text();
        console.log("Response error text:", errorText);
        throw new Error(`Failed to analyze weight data: ${errorText}`);
      }

      const data = await response.json();
      console.log("Response data:", data);
      setResult(data);
    } catch (error) {
      console.error("Fetch error:", error);
      setError(
        error.message.includes("Failed to fetch")
          ? "Unable to connect to the server. Please try again later."
          : error.message
      );
    } finally {
      setLoading(false);
    }
  };
  

  // Scroll to the chart when the result is updated
  useEffect(() => {
    if (result && chartRef.current) {
      chartRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [result]); // Trigger when result changes

  return (
    <div className="min-h-screen w-screen bg-gradient-to-b from-white to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-white rounded-2xl shadow-xl p-8 text-center mx-4 relative">
        <h1 className="text-3xl sm:text-4xl font-semibold text-gray-800 mb-4">
          Track Your Weight Data
        </h1>
        <p className="text-gray-600 mb-6 text-base sm:text-lg">
          Measure your progress and predict your weight loss journey.
        </p>

        <FileUploadBox
          accept=".csv,.xlsx"
          onFileSelect={handleFileSelect}
          labelText="Drag & drop CSV file here or click to choose"
        />

        <button
          onClick={handleUpload}
          className="mt-4 w-full bg-white text-black px-6 py-3 rounded-full hover:bg-gray-100 transition duration-200 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Processing..." : "Analyze Weight Data"}
        </button>

        {error && (
          <div className="mt-6 text-left text-red-500">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-6">
            <div className="text-left">
              <h2 className="text-xl font-semibold mb-2 text-gray-800">Weight Analysis:</h2>
              <p className="text-xl font-semibold text-gray-800">
                {result.message}
              </p>
            </div>
            <div ref={chartRef}> {/* Add ref to the chart container */}
              {result.historical && result.predicted ? (
                <WeightChart historical={result.historical} predicted={result.predicted} />
              ) : (
                <p className="text-gray-600 mt-2">No chart data available.</p>
              )}
            </div>
          </div>
        )}

        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 rounded-2xl">
            <RingLoader
              color="#007AFF"
              size={90}
              speedMultiplier={1.2}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default WeightDataPage;