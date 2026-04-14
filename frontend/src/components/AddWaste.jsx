import React, { useEffect, useMemo, useState } from "react";
import { BadgeCheck, Clock3, Loader2, MapPin, Star, Upload } from "lucide-react";
import api from "../api/axios";

const cardBaseClass =
  "rounded-xl border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:bg-gray-50";

const AddWaste = ({ onSubmitted }) => {
  const [imageFile, setImageFile] = useState(null);
  const [proofFile, setProofFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [facilitiesLoading, setFacilitiesLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [facilitiesError, setFacilitiesError] = useState("");
  const [success, setSuccess] = useState("");
  const [facilities, setFacilities] = useState([]);
  const [aiQuestions, setAiQuestions] = useState([]);
  const [userAnswers, setUserAnswers] = useState({});
  const [analysis, setAnalysis] = useState({
    item_name: "",
    material: "",
    estimated_weight: "",
    size: "Medium",
    condition: "Mixed",
    verification_questions: [],
  });

  const parseQuantityGrams = (value) => {
    const parsedNumber = Number.parseFloat(String(value).replace(/[^\d.]/g, ""));
    if (!Number.isFinite(parsedNumber) || parsedNumber <= 0) return 100;
    const lower = String(value).toLowerCase();
    if (lower.includes("kg")) return parsedNumber * 1000;
    return parsedNumber;
  };

  const canSubmit = useMemo(() => Boolean(imageFile) && !loading, [imageFile, loading]);
  const canFinalSubmit = useMemo(
    () => Boolean(analysis.item_name.trim()) && Boolean(proofFile) && !submitting,
    [analysis.item_name, proofFile, submitting],
  );
  const pendingPoints = useMemo(() => {
    const grams = parseQuantityGrams(analysis.estimated_weight);
    return Math.max(5, Math.round(grams / 50));
  }, [analysis.estimated_weight]);

  const resetAll = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setImageFile(null);
    setProofFile(null);
    setPreviewUrl("");
    setFacilities([]);
    setAiQuestions([]);
    setUserAnswers({});
    setFacilitiesError("");
    setAnalysis({
      item_name: "",
      material: "",
      estimated_weight: "",
      size: "Medium",
      condition: "Mixed",
      verification_questions: [],
    });
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setError("Please upload an image file only.");
      return;
    }
    setError("");
    setSuccess("");
    setImageFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleAnalyze = async (event) => {
    event.preventDefault();
    if (!imageFile) return;

    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const formData = new FormData();
      formData.append("file", imageFile);

      const response = await api.post("/waste/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const payload = response?.data ?? {};
      const detected = payload.analysis ?? {};
      const detectedQuestions = Array.isArray(detected.verification_questions)
        ? detected.verification_questions
        : [];
      const verificationQuestions = detectedQuestions.slice(0, 4);

      setAnalysis({
        item_name: detected.item_name || "",
        material: detected.material || "",
        estimated_weight: detected.estimated_weight || "",
        size: detected.size || "Medium",
        condition: detected.condition || "Mixed",
        verification_questions: verificationQuestions,
      });
      setAiQuestions(verificationQuestions);
      setUserAnswers({});
      setFacilities([]);
      setFacilitiesError("");
    } catch {
      setError("Unable to analyze image right now.");
      setFacilities([]);
      setAiQuestions([]);
      setUserAnswers({});
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const selectedMaterial = analysis.material.trim();
    if (!selectedMaterial) {
      setFacilities([]);
      setFacilitiesError("");
      return;
    }

    const fetchNearbyFacilities = async () => {
      setFacilitiesLoading(true);
      setFacilitiesError("");
      try {
        const response = await api.get("/facilities/nearby", {
          params: {
            lat: 23.2156,
            lon: 72.6369,
            material: selectedMaterial,
          },
        });
        const nearby = response?.data?.facilities ?? response?.data?.data ?? response?.data ?? [];
        setFacilities(Array.isArray(nearby) ? nearby : []);
      } catch {
        setFacilities([]);
        setFacilitiesError("Could not load nearby facilities for this material.");
      } finally {
        setFacilitiesLoading(false);
      }
    };

    fetchNearbyFacilities();
  }, [analysis.material]);

  const handleFinalSubmit = async (event) => {
    event.preventDefault();
    if (!analysis.item_name.trim()) {
      setError("Item Name is required before submitting.");
      return;
    }

    setSubmitting(true);
    setError("");
    setSuccess("");
    try {
      const verificationPayload = JSON.stringify(
        aiQuestions.map((question, index) => ({
          question,
          answer: userAnswers[index] || "",
        })),
      );
      const formData = new FormData();
      formData.append("item_name", analysis.item_name.trim());
      formData.append("quantity_grams", String(Number(parseQuantityGrams(analysis.estimated_weight))));
      formData.append("item_type", analysis.material || "Other");
      formData.append("condition", analysis.condition || "Mixed");
      formData.append("verification_payload", verificationPayload);
      formData.append("receipt_proof", proofFile);

      await api.post("/waste/add", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSuccess(
        `Drop-off proof submitted. +${pendingPoints} points are now pending verification.`,
      );
      resetAll();
      if (onSubmitted) onSubmitted();
    } catch {
      setError("Unable to submit drop-off verification right now.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className={`${cardBaseClass} p-5`}>
      <h2 className="text-base font-semibold text-slate-900">AI Waste Detection</h2>
      <p className="mt-1 text-sm text-gray-600">
        Upload a waste image to detect material and get relevant facilities.
      </p>

      <form className="mt-4 space-y-4" onSubmit={handleAnalyze}>
        <div>
          <label className="mb-1 block text-sm text-gray-700">Image Upload</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-slate-900 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        {previewUrl && (
          <img
            src={previewUrl}
            alt="Waste preview"
            className="h-56 w-full rounded-xl border border-gray-200 object-cover"
          />
        )}

        <button
          type="submit"
          disabled={!canSubmit}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              AI is analyzing...
            </>
          ) : (
            <>
              <Upload className="h-4 w-4" />
              Analyze Image
            </>
          )}
        </button>
      </form>

      {error && <p className="mt-3 text-sm text-red-500">{error}</p>}
      {success && <p className="mt-3 text-sm text-emerald-700">{success}</p>}

      {(analysis.item_name || analysis.material) && (
        <div className="mt-6 space-y-5">
          <div className="rounded-xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-white p-4 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-emerald-900">Step 1: Review AI Appraisal</h3>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">
                <BadgeCheck className="h-3.5 w-3.5" />
                Pending Points: +{pendingPoints}
              </span>
            </div>
            <p className="mt-1 text-xs text-emerald-700">
              AI suggestions are editable. Update details before confirming your drop-off proof.
            </p>

            <form className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2" onSubmit={handleFinalSubmit}>
              <input
                value={analysis.item_name}
                onChange={(event) =>
                  setAnalysis((prev) => ({ ...prev, item_name: event.target.value }))
                }
                placeholder="Detected Item Name"
                className="rounded-lg border border-emerald-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
              <input
                value={analysis.material}
                onChange={(event) =>
                  setAnalysis((prev) => ({ ...prev, material: event.target.value }))
                }
                placeholder="Detected Material"
                className="rounded-lg border border-emerald-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
              <input
                value={analysis.estimated_weight}
                onChange={(event) =>
                  setAnalysis((prev) => ({ ...prev, estimated_weight: event.target.value }))
                }
                placeholder="Estimated Weight (e.g., 250g)"
                className="rounded-lg border border-emerald-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
              <select
                value={analysis.size}
                onChange={(event) => setAnalysis((prev) => ({ ...prev, size: event.target.value }))}
                className="rounded-lg border border-emerald-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="Small">Small</option>
                <option value="Medium">Medium</option>
                <option value="Large">Large</option>
              </select>
              <select
                value={analysis.condition}
                onChange={(event) =>
                  setAnalysis((prev) => ({ ...prev, condition: event.target.value }))
                }
                className="rounded-lg border border-emerald-200 bg-white px-3 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="Clean">Clean</option>
                <option value="Dirty">Dirty</option>
                <option value="Mixed">Mixed</option>
              </select>

              {aiQuestions.length > 0 && (
                <div className="sm:col-span-2 rounded-lg border border-emerald-200 bg-emerald-50/80 p-3">
                  <h4 className="text-sm font-semibold text-emerald-900">🤖 AI Appraiser Follow-up</h4>
                  <div className="mt-3 space-y-3">
                    {aiQuestions.map((question, index) => (
                      <div key={`${question}-${index}`}>
                        <label
                          htmlFor={`ai-question-${index}`}
                          className="mb-1 block text-sm font-medium text-emerald-900"
                        >
                          {question}
                        </label>
                        <input
                          id={`ai-question-${index}`}
                          type="text"
                          value={userAnswers[index] || ""}
                          onChange={(event) =>
                            setUserAnswers((prev) => ({
                              ...prev,
                              [index]: event.target.value,
                            }))
                          }
                          placeholder="Add your response..."
                          className="w-full rounded-lg border border-emerald-200 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="sm:col-span-2 rounded-lg border border-emerald-200 bg-white p-3">
                <h4 className="text-sm font-semibold text-emerald-900">Step 2: Verify Drop-off</h4>
                <p className="mt-1 text-xs text-emerald-700">
                  Upload Receipt/Proof of Drop-off to Claim Points
                </p>
                <label className="mt-3 block">
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(event) => setProofFile(event.target.files?.[0] || null)}
                    className="w-full rounded-lg border border-emerald-200 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </label>
                {proofFile && (
                  <p className="mt-2 text-xs text-emerald-700">Attached: {proofFile.name}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={!canFinalSubmit}
                className="sm:col-span-2 inline-flex items-center justify-center rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {submitting ? "Submitting proof..." : "Claim Pending Points"}
              </button>
            </form>
          </div>

          <div className="rounded-xl border border-emerald-200 bg-white p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900">Nearby Facilities (Auto-Matched)</h3>
            <p className="mt-1 text-xs text-gray-600">
              Based on selected material:{" "}
              <span className="font-medium text-emerald-700">{analysis.material || "N/A"}</span>
            </p>
            {facilitiesError && <p className="mt-2 text-sm text-red-500">{facilitiesError}</p>}
            <div className="mt-3 space-y-3">
              {facilitiesLoading ? (
                <p className="text-sm text-gray-500">Loading nearby facilities...</p>
              ) : facilities.length === 0 ? (
                <p className="text-sm text-gray-500">No matching facilities found nearby.</p>
              ) : (
                facilities.map((facility, index) => {
                  const distance = facility.distance_km ?? facility.distance ?? "N/A";
                  const rating = facility.rating ?? "N/A";
                  const isOpen = Boolean(facility.is_open_now ?? facility.open_now);
                  return (
                    <div
                      key={facility.id || facility.name || index}
                      className="rounded-xl border border-emerald-100 bg-emerald-50/40 p-3 shadow-sm"
                    >
                      <p className="text-sm font-semibold text-slate-900">
                        {facility.name || "Recycling Facility"}
                      </p>
                      <p className="mt-0.5 text-xs text-gray-600">{facility.address || "Address unavailable"}</p>
                      <div className="mt-2 flex flex-wrap gap-2 text-xs">
                        <span className="inline-flex items-center gap-1 rounded-full bg-white px-2 py-1 text-slate-700">
                          <MapPin className="h-3.5 w-3.5 text-emerald-600" />
                          {distance} km
                        </span>
                        <span className="inline-flex items-center gap-1 rounded-full bg-white px-2 py-1 text-slate-700">
                          <Star className="h-3.5 w-3.5 text-amber-500" />
                          {rating}
                        </span>
                        <span
                          className={`inline-flex items-center gap-1 rounded-full px-2 py-1 ${
                            isOpen ? "bg-emerald-100 text-emerald-800" : "bg-gray-100 text-gray-700"
                          }`}
                        >
                          <Clock3 className="h-3.5 w-3.5" />
                          {isOpen ? "Open Now" : "Closed"}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default AddWaste;
