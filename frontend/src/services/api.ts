/**
 * Lightweight wrapper around the Fetch API for consistent HTTP requests
 */

const BASE_URL = "https://api.example.com"; // TODO: Replace with actual API base URL

/**
 * Sends a request to the specified API endpoint.
 *
 * @param endpoint - API endpoint (without base URL)
 * @param options - Optional fetch configuration (method, headers, body, etc.)
 * @returns Parsed JSON response data
 * @throws Error if the response is not OK (non-2xx status)
 */
export async function apiRequest(endpoint: string, options: RequestInit = {}){
    const response  = await fetch(`${BASE_URL}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || 'API request failed');
  }

  return response.json();   
}