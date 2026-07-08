import { useState } from "react";
import api from "../services/api";
import "./createticket.css";

function CreateTicket() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!title || !description) {
      alert("Please fill all fields.");
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem("token");

      const response = await api.post(
        "/tickets/",
        {
          title,
          description,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log(response.data);

      alert("Ticket Created Successfully!");

      setTitle("");
      setDescription("");
    } catch (error) {
      console.log("Status:",error.response?.status);
      console.log("Data:",error.response?.data);
      alert(JSON.stringify(error.response?.data));
      alert("Unable to create ticket");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="form-card">
        <h2>Create Ticket</h2>

        <input
          type="text"
          placeholder="Ticket Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <textarea
          rows="8"
          placeholder="Describe your issue"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <button onClick={handleCreate} disabled={loading}>
          {loading ? "AI is Classifying Ticket..." : "Create Ticket"}
        </button>

        {loading && (
          <p
            style={{
              marginTop: "15px",
              color: "#2563eb",
              textAlign: "center",
              fontWeight: "bold",
            }}
          >
             Please wait while the AI classifies your ticket...
          </p>
        )}
      </div>
    </div>
  );
}

export default CreateTicket;