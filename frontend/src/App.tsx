import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const DataAnalysis = lazy(() => import("./pages/DataAnalysis"));
const Prediction = lazy(() => import("./pages/Prediction"));
const SmartBinIot = lazy(() => import("./pages/SmartBinIot"));
const ModelPerformance = lazy(() => import("./pages/ModelPerformance"));
const About = lazy(() => import("./pages/About"));

export default function App() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-bg px-6 py-8 text-sm text-muted">Memuat halaman...</div>}>
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
    </Suspense>
  );
}
