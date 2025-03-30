import { useState, useEffect } from "react";
import FileUploadBox from "../components/FileUploadBox";

const backgrounds = [
  { image: "https://images.pexels.com/photos/40568/medical-appointment-doctor-healthcare-40568.jpeg" },
  { image: "https://images.pexels.com/photos/5214962/pexels-photo-5214962.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1" },
  { image: "https://t4.ftcdn.net/jpg/01/33/33/41/360_F_133334155_X23HzbJKawbIgXVaub4bPM8CjpkS5uMS.jpg" },
];

function HealthDataPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [nextIndex, setNextIndex] = useState(1);
  const [isTransitioning, setIsTransitioning] = useState(false);

  document.title = "Quack Hacks - Health Summary";

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
  };

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
      setResult(data);
    } catch (err) {
      console.error("Upload failed", err);
      setResult({ error: "Failed to fetch insights." });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setIsTransitioning(true);

      setTimeout(() => {
        setCurrentIndex(nextIndex);
        setNextIndex((prev) => (prev + 1) % backgrounds.length);
        setIsTransitioning(false);
      }, 1000);
    }, 8000); // Change every 10 seconds

    return () => clearInterval(interval);
  }, [nextIndex]);

  return (
    <div className="relative min-h-screen w-screen flex items-center justify-center overflow-hidden">
      {/* Background Layers */}
      <div className="background-container">
        <div
          className={`background-layer ${isTransitioning ? "bg-transition-out" : ""}`}
          style={{ backgroundImage: `url(${backgrounds[currentIndex].image})` }}
        />
        {isTransitioning && (
          <div
            className="background-layer bg-transition-in"
            style={{ backgroundImage: `url(${backgrounds[nextIndex].image})` }}
          />
        )}
      </div>

      {/* Content Box */}
      <div className="relative z-10 w-full max-w-3xl bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8 text-center mx-4">
        <h1 className="text-3xl sm:text-4xl font-semibold text-gray-800 mb-4">
          Import Your Apple Health Data
        </h1>
        <p className="text-gray-500 mb-6 text-base sm:text-lg">
          Unlock valuable insights into your well-being.
        </p>

        <FileUploadBox accept=".csv,.xlsx" onFileSelect={handleFileSelect} labelText="Drag & drop file here or click to choose" />

        <button
          onClick={handleUpload}
          className="mt-4 w-full bg-black text-white px-6 py-3 rounded-full hover:bg-gray-800 transition duration-200"
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
