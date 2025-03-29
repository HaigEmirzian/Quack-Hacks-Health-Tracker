import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HealthDataPage from "./pages/HealthDataPage";
import WeightDataPage from "./pages/WeightDataPage";
import Navbar from "./components/Navbar";

function App() {
  return (
    <Router>
      <div className="bg-gray-100">
        <Navbar />
        <Routes>
          <Route path="/" element={<HealthDataPage />} />
          <Route path="/weight" element={<WeightDataPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
