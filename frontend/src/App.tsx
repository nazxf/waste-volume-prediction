import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import DataAnalysis from "./pages/DataAnalysis";
import Prediction from "./pages/Prediction";
import SmartBinIot from "./pages/SmartBinIot";
import ModelPerformance from "./pages/ModelPerformance";
import About from "./pages/About";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analisis" element={<DataAnalysis />} />
        <Route path="/prediksi" element={<Prediction />} />
        <Route path="/smart-bin" element={<SmartBinIot />} />
        <Route path="/model" element={<ModelPerformance />} />
        <Route path="/tentang" element={<About />} />
      </Route>
    </Routes>
  );
}
