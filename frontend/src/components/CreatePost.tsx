import { useState } from 'react';
import { postService } from '../services/api';

interface CreatePostProps {
  onPostCreated: () => void;
}

export default function CreatePost({ onPostCreated }: CreatePostProps) {
  const [caption, setCaption] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await postService.uploadPost(file, caption);
      setCaption('');
      setFile(null);
      setPreview('');
      onPostCreated();
      alert('Post created successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Create Post</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Caption
          </label>
          <textarea
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none resize-none"
            placeholder="What's on your mind?"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Image or Video
          </label>
          <input
            type="file"
            onChange={handleFileChange}
            accept="image/*,video/*"
            required
            className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100 cursor-pointer"
          />
        </div>

        {preview && (
          <div className="relative">
            {file?.type.startsWith('video/') ? (
              <video
                src={preview}
                controls
                className="w-full max-h-96 rounded-lg object-contain bg-gray-100"
              />
            ) : (
              <img
                src={preview}
                alt="Preview"
                className="w-full max-h-96 rounded-lg object-contain bg-gray-100"
              />
            )}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
        >
          {loading ? 'Posting...' : 'Post'}
        </button>
      </form>
    </div>
  );
}
