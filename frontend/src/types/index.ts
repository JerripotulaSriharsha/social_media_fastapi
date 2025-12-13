export interface User {
  id: string;
  email: string;
}

export interface Post {
  id: string;
  caption: string;
  url: string;
  file_type: 'image' | 'video';
  file_name: string;
  created_at: string;
  user_id?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}
