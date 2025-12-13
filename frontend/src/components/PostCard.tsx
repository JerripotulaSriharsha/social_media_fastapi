import { useState } from 'react';
import type { Post } from '../types';
import { postService } from '../services/api';

interface PostCardProps {
  post: Post;
  onPostUpdated: () => void;
  onPostDeleted: () => void;
}

export default function PostCard({ post, onPostUpdated, onPostDeleted }: PostCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [caption, setCaption] = useState(post.caption);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await postService.updatePost(post.id, caption, file || undefined);
      setIsEditing(false);
      setFile(null);
      setPreview('');
      onPostUpdated();
      alert('Post updated successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update post');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this post?')) return;

    setLoading(true);
    try {
      await postService.deletePost(post.id);
      onPostDeleted();
      alert('Post deleted successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete post');
    } finally {
      setLoading(false);
    }
  };

  if (isEditing) {
    return (
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <form onSubmit={handleUpdate} className="p-4 space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Edit Post</h3>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Caption
            </label>
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Change file (optional)
            </label>
            <input
              type="file"
              onChange={handleFileChange}
              accept="image/*,video/*"
              className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
            />
          </div>

          {preview && (
            <div className="relative">
              {file?.type.startsWith('video/') ? (
                <video src={preview} controls className="w-full max-h-64 rounded-lg" />
              ) : (
                <img src={preview} alt="Preview" className="w-full max-h-64 rounded-lg object-cover" />
              )}
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-purple-700 transition disabled:opacity-50"
            >
              {loading ? 'Updating...' : 'Update'}
            </button>
            <button
              type="button"
              onClick={() => {
                setIsEditing(false);
                setCaption(post.caption);
                setFile(null);
                setPreview('');
              }}
              className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow">
      <div className="relative">
        {post.file_type === 'video' ? (
          <video
            src={post.url}
            controls
            className="w-full h-80 object-cover bg-gray-100"
          />
        ) : (
          <img
            src={post.url}
            alt={post.file_name}
            className="w-full h-80 object-cover bg-gray-100"
          />
        )}
      </div>

      <div className="p-4">
        <p className="text-gray-800 mb-3 whitespace-pre-wrap">{post.caption}</p>
        <div className="text-sm text-gray-500 mb-3">
          {new Date(post.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            className="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-600 transition"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={loading}
            className="flex-1 bg-red-500 text-white py-2 px-4 rounded-lg font-medium hover:bg-red-600 transition disabled:opacity-50"
          >
            {loading ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}
