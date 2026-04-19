const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface DBDocument {
  id: number;
  titre: string;
  contenu_json: any;
  date_creation: string;
}

export interface SearchResult {
  id: number;
  titre: string;
  resumen_ia: string | null;
  tipo_documento: string | null;
  score: number;
}

/**
 * Centeralized API Client to interact with the FastAPI backend.
 */
export const apiClient = {
  /**
   * Fetches latest analyzed documents.
   */
  async getDocuments(limit = 10, offset = 0): Promise<DBDocument[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/documents?limit=${limit}&offset=${offset}`, {
        cache: "no-store", // Ensure we get fresh data from the API
      });
      if (!response.ok) throw new Error("Failed to fetch documents");
      return await response.json();
    } catch (error) {
      console.error("API Error (getDocuments):", error);
      return [];
    }
  },

  /**
   * Fetches a single document by ID.
   */
  async getDocument(id: number | string): Promise<DBDocument | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
        cache: "no-store",
      });
      if (!response.ok) return null;
      return await response.json();
    } catch (error) {
      console.error(`API Error (getDocument ${id}):`, error);
      return null;
    }
  },

  /**
   * Performs full-text search using ParadeDB via the API.
   */
  async searchDocuments(query: string): Promise<SearchResult[]> {
    if (!query || query.length < 2) return [];
    try {
      const response = await fetch(`${API_BASE_URL}/documents/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error("Search failed");
      return await response.json();
    } catch (error) {
      console.error("API Error (searchDocuments):", error);
      return [];
    }
  }
};
