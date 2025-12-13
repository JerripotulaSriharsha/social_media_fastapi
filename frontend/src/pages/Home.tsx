import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, postService } from '../services/api';
import type { Post } from '../types';
import CreatePost from '../components/CreatePost';
import PostCard from '../components/PostCard';

export default function Home() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const data = await postService.getFeed();
      setPosts(data);
      setError('');
    } catch (err: any) {
      if (err.response?.status === 401) {
        authService.logout();
        navigate('/auth');
      } else {
        setError('Failed to load feed');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      navigate('/auth');
      return;
    }
    fetchPosts();
  }, [navigate]);

  const handleLogout = () => {
    authService.logout();
    navigate('/auth');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            📱 Social Media
          </h1>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-600 transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        <CreatePost onPostCreated={fetchPosts} />

        <div className="mb-4">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Feed</h2>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            <p className="text-gray-600 mt-4">Loading feed...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-center">
            {error}
          </div>
        ) : posts.length === 0 ? (
          <div className="bg-white rounded-xl shadow-md p-12 text-center">
            <p className="text-gray-600 text-lg">No posts yet. Be the first to post!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {posts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                onPostUpdated={fetchPosts}
                onPostDeleted={fetchPosts}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
