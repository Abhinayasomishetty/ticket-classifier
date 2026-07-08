import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";
import "./login.css";

function Register() {

    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);

    const handleRegister = async () => {

        setLoading(true);

        try {

            await api.post("/auth/register", {
                username,
                email,
                password
            });

            alert("Registration Successful!");

            navigate("/");

        } catch (error) {

            console.log(error.response?.data);
            alert("Registration Failed");

        } finally {

            setLoading(false);

        }

    };

    return (

        <div className="login-container">

            <div className="login-card">

                <h1> AI Ticket Classifier</h1>

                <p className="subtitle">
                    Create your account
                </p>

                <h3>Register</h3>

                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e)=>setUsername(e.target.value)}
                />

                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e)=>setEmail(e.target.value)}
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e)=>setPassword(e.target.value)}
                />

                <button
                    onClick={handleRegister}
                    disabled={loading}
                >
                    {loading ? "Creating Account..." : "Register"}
                </button>

                <p>
                    Already have an account?{" "}
                    <Link to="/">Login</Link>
                </p>

            </div>

        </div>

    );

}

export default Register;