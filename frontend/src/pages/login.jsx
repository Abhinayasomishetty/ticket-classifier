import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";
import "./login.css";

function Login() {

    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);

    const handleLogin = async () => {

        setLoading(true);

        try {

            const formData = new URLSearchParams();

            formData.append("username", email);
            formData.append("password", password);

            const response = await api.post(
                "/auth/login",
                formData,
                {
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                }
            );

            localStorage.setItem("token", response.data.access_token);

            navigate("/dashboard");

        } catch (error) {

            console.log(error.response?.data);

            alert("Invalid Email or Password");

        } finally {

            setLoading(false);

        }
    };

    return (

        <div className="login-container">

            <div className="login-card">

                <h1> AI Ticket Classifier</h1>

                <p className="subtitle">
                    Smart IT Support powered by AI
                </p>

                <h3>Login</h3>

                <input
                    type="email"
                    placeholder="Enter Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />

                <input
                    type="password"
                    placeholder="Enter Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button
                    onClick={handleLogin}
                    disabled={loading}
                >
                    {loading ? "Signing In..." : "Login"}
                </button>

                <p>
                    Don't have an account?{" "}
                    <Link to="/register">
                        Register
                    </Link>
                </p>

            </div>

        </div>

    );
}

export default Login;
