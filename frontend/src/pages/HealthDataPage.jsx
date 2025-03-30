import { useState } from "react";
import FileUploadBox from "../components/FileUploadBox";

function HealthDataPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const res = await fetch("http://localhost:5000/appleDataUpload", {
        method: "POST",
        body: formData,
      });
  
      if (!res.ok) {
        const errorData = await res.json();
        setResult({ error: errorData.error || "An unknown error occurred." });
      } else {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error("Upload failed", err);
      setResult({ error: "Failed to fetch insights." });
    } finally {
      setLoading(false);
    }
  };  

  return (
    <div className="min-h-screen w-screen bg-gradient-to-b from-white to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-white rounded-2xl shadow-xl p-8 text-center mx-4">
        <h1 className="text-3xl sm:text-4xl font-semibold text-gray-800 mb-4">
          Import Your Apple Health Data
        </h1>
        <p className="text-gray-500 mb-6 text-base sm:text-lg">
          Unlock valuable insights into your well-being.
        </p>

        <FileUploadBox
          accept=".xml"
          onFileSelect={handleFileSelect}
          labelText="Drag & drop file here or click to choose"
        />

        <button
          onClick={handleUpload}
          className="mt-4 w-full bg-white text-black px-6 py-3 rounded-full hover:bg-gray-100 transition duration-200"
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Get Insights"}
        </button>

        {result && (
          <div className="mt-6 text-left">
            <h2 className="text-xl font-semibold mb-2">Results:</h2>
            <pre className="bg-gray-100 p-4 rounded-lg text-sm text-gray-800 overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default HealthDataPage;
