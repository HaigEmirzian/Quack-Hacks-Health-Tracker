import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/prediction", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setInsights(data);
    } catch (err) {
      console.error("Upload failed", err);
      setInsights({ error: "Failed to fetch insights." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen bg-gradient-to-b from-white to-gray-100 flex items-center justify-center">
      <div className="w-full max-w-3xl bg-white rounded-2xl shadow-xl p-8 text-center mx-4">
        <h1 className="text-3xl sm:text-4xl font-semibold text-gray-800 mb-4">
          Import Your Apple Health Data
        </h1>
        <p className="text-gray-500 mb-6 text-base sm:text-lg">
          Unlock valuable insights into your well-being.
        </p>

        {/* Big File Input Box */}
        <label
          htmlFor="file-upload"
          className="block border-4 border-dashed border-gray-300 rounded-lg h-48 flex flex-col items-center justify-center cursor-pointer hover:border-black transition duration-200 bg-gray-50"
        >
          <span className="text-xl text-gray-700">
            {file ? file.name : "Drag & drop file here or click to choose"}
          </span>
          <input
            id="file-upload"
            type="file"
            accept=".csv,.xlsx"
            onChange={(e) => setFile(e.target.files[0])}
            className="hidden"
          />
        </label>

        <button
          onClick={handleUpload}
          className="mt-4 w-full bg-black text-white px-6 py-3 rounded-full hover:bg-gray-800 transition duration-200"
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Get Insights"}
        </button>

        {insights && (
          <div className="mt-6 text-left">
            <h2 className="text-xl font-semibold mb-2">Results:</h2>
            <pre className="bg-gray-100 p-4 rounded-lg text-sm text-gray-800 overflow-x-auto">
              {JSON.stringify(insights, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
