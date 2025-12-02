/**
 * Auth Service - Centralized authentication API calls
 * Handles all authentication-related HTTP requests
 */

const AUTH_BASE =
  process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000/api/v1/auth";

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
  username: string;
}

export const authService = {
  /**
   * Authenticate user and retrieve access tokens
   */
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await fetch(`${AUTH_BASE}/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const status = response.status;
      let message = "Login failed";
      if (status === 401) {
        message = "Invalid username or password";
      } else if (status >= 500) {
        message = "Server error. Please try again later";
      } else {
        // Try to include more details if available
        const errorText = await response.text();
        message = errorText || `Login failed (status ${status}: ${response.statusText})`;
      }
      throw new Error(message);
    }

    return response.json();
  },

  /**
   * Register a new user account
   */
  async register(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await fetch(`${AUTH_BASE}/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Registration failed");
    }

    return response.json();
  },

  /**
   * Logout user and invalidate refresh token
   */
  async logout(refreshToken: string, accessToken: string): Promise<void> {
    try {
      await fetch(`${AUTH_BASE}/logout/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });
    } catch (err) {
      console.error("Logout API error:", err);
    }
  },

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await fetch(`${AUTH_BASE}/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      const status = response.status;
      if (status === 401) {
        throw new Error("Session expired. Please log in again");
      } else if (status >= 500) {
        throw new Error("Server error. Please try again later");
      }
      throw new Error("Token refresh failed");
    }

    return response.json();
  },
};
