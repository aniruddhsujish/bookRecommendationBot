"use client";

import { useState } from "react";
import Image from "next/image";

interface Book {
    book_id: string;
    title: string;
    authors: string[];
    description: string;
    thumbnail: string;
    score: string;
    explanation: {
        similar: string[];
        different: string[];
        recommended_because: string;
    };
}

interface RecommendResponse {
    query_book: Book;
    recommendations: Book[];
}
export default function Home() {
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<RecommendResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [discoverResults, setDiscoverResults] = useState<Book[]>([]);
    const [discoverLoading, setDiscoverLoading] = useState(false);

    async function handleSearch() {
        if (!query.trim()) return;
        setLoading(true);
        setError(null);
        setResults(null);

        try {
            const response = await fetch(
                "http://localhost:8000/api/recommend",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title: query, limit: 5 }),
                },
            );

            if (!response.ok) {
                setError("Book not found,. Try a different title.");
                return;
            }

            const data = await response.json();
            setResults(data);

            await handleRate(data.query_book.book_id, data.query_book.title, 1);
        } catch {
            setError("Could not connect to server");
        } finally {
            setLoading(false);
        }
    }

    async function handleRate(bookId: string, title: string, rating: number) {
        await fetch("http://localhost:8000/api/rate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ book_id: bookId, title, rating }),
        });
    }

    async function handleDiscover() {
        setDiscoverLoading(true);
        try {
            const response = await fetch(
                "http://localhost:8000/api/discover?limit=5",
            );
            const data = await response.json();
            console.log(data);
            setDiscoverResults(data?.books ?? []);
        } finally {
            setDiscoverLoading(false);
        }
    }

    return (
        <main className="min-h-screen bg-gray-50">
            <div className="max-w-4xl mx-auto px-6 py-16">
                <h1 className="text-4x1 font-bold text-gray-900 mb-2">
                    ShelfSense
                </h1>
                <p className="text-gray-500 mb-12">
                    Find books similar to ones you love
                </p>

                {/* Search section */}
                <div className="bg-white rounded-2x1 shadow-sm border border-gray-100 p-8 mb-8">
                    <h2 className="text-lg font-semibold text-gray-700 mb-4">
                        Find similar books
                    </h2>
                    <div className="flex gap-3">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) =>
                                e.key === "Enter" && handleSearch()
                            }
                            placeholder="Enter a book title..."
                            className="flex-1 border border-gray-200 rounded-lg px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                            onClick={handleSearch}
                            disabled={loading}
                            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                        >
                            {loading ? "Searching..." : "Search"}
                        </button>
                    </div>

                    {error && (
                        <p className="text-red-500 text-sm mt-3">{error}</p>
                    )}
                </div>

                {/* Results */}
                {results && (
                    <div className="space-y-4">
                        <h2 className="text-lg font-semibold text-gray-700">
                            Books similar to{" "}
                            <span className="text-blue-600">
                                {results.query_book.title}
                            </span>
                        </h2>
                        {results.recommendations.map((book) => (
                            <div
                                key={book.book_id}
                                className="bg-white rounded-2x1 shadow-sm border border-gray-100 p-6"
                            >
                                <div className="flex gap=4">
                                    {book.thumbnail && (
                                        <div className="relative w-16 h-24 flex-shrink-0">
                                            <Image
                                                src={book.thumbnail.replace(
                                                    "http://",
                                                    "https://",
                                                )}
                                                alt={book.title}
                                                fill
                                                className="object-cover rounded-lg"
                                            />
                                        </div>
                                    )}
                                    <div className="flex-1 ml-4">
                                        <h3 className="font-semibold text-gray-900">
                                            {book.title}
                                        </h3>
                                        <p className="text-gray-400 text-sm mb-3">
                                            {book.authors.join(", ")}
                                        </p>
                                        <p className="text-gray-600 text-sm leading-relaxed">
                                            {
                                                book.explanation
                                                    .recommended_because
                                            }
                                        </p>
                                        <details className="text-sm">
                                            <summary className="text-blue-500 cursor-pointer hover:text-blue-700 font-medium">
                                                Why this book?
                                            </summary>
                                            <div className="mt-3 space-y-3">
                                                <div>
                                                    <p className="font-medium text-gray-700 mb-1">
                                                        Similar
                                                    </p>
                                                    <ul className="space-y-1">
                                                        {book.explanation.similar.map(
                                                            (point, i) => (
                                                                <li
                                                                    key={i}
                                                                    className="text-gray-500 flex gap-2"
                                                                >
                                                                    <span className="text-green-400">
                                                                        ✓
                                                                    </span>{" "}
                                                                    {point}
                                                                </li>
                                                            ),
                                                        )}
                                                    </ul>
                                                </div>
                                                <div>
                                                    <p className="font-medium text-gray-700 mb-1">
                                                        Different
                                                    </p>
                                                    <ul className="space-y-1">
                                                        {book.explanation.different.map(
                                                            (point, i) => (
                                                                <li
                                                                    key={i}
                                                                    className="text-gray-500 flex gap-2"
                                                                >
                                                                    <span className="text-orange-400">
                                                                        ≠
                                                                    </span>{" "}
                                                                    {point}
                                                                </li>
                                                            ),
                                                        )}
                                                    </ul>
                                                </div>
                                            </div>
                                        </details>
                                        <div className="flex gap-3 mt-4 pt-4 border-t border-gray-100">
                                            <button
                                                onClick={() =>
                                                    handleRate(
                                                        book.book_id,
                                                        book.title,
                                                        1,
                                                    )
                                                }
                                                className="flex items-center gap-1 text-sm text-gray-400 hover:text-green-500 transition-colors"
                                            >
                                                👍 Like
                                            </button>
                                            <button
                                                onClick={() =>
                                                    handleRate(
                                                        book.book_id,
                                                        book.title,
                                                        -1,
                                                    )
                                                }
                                                className="flex items-center gap-1 text-sm text-gray-400 hover:text-red-400 transition-colors"
                                            >
                                                👎 Dislike
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
                {/* Discover section */}
                <div className="bg-white rounded-2x1 shadow-sm border border-gray-100 p-8">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h2 className="text-lf font-semibold text-gray-700">
                                Discover for you
                            </h2>
                            <p className="text-gray-400 text-sm">
                                Based on your taste profile
                            </p>
                        </div>
                        <button
                            onClick={handleDiscover}
                            disabled={discoverLoading}
                            className="bg-blue-600 text0white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
                        >
                            {discoverLoading ? "Loading..." : "Refresh"}
                        </button>
                    </div>

                    {discoverResults?.length === 0 ? (
                        <p className="text-gray-400 text-sm">
                            Rate some books to get personalised recommendations
                        </p>
                    ) : (
                        <div className="space-y-4">
                            {discoverResults?.map((book) => (
                                <div
                                    key={book.book_id}
                                    className="flex gap-4 py-4 border-t border-gray-50"
                                >
                                    {book.thumbnail && (
                                        <div className="relative w-12 h-16 flex-shrink-0">
                                            <Image
                                                src={book.thumbnail.replace(
                                                    "http://",
                                                    "https://",
                                                )}
                                                alt={book.title}
                                                fill
                                                className="object-cover rounded"
                                            />
                                        </div>
                                    )}
                                    <div className="flex-1 ml-2">
                                        <h3 className="font-medium text-gray-900 text-sm">
                                            {book.title}
                                        </h3>
                                        <p className="text-gray-400 text-xs mb-2">
                                            {book.authors.join(", ")}
                                        </p>
                                        <p className="text-gray-500 text-xs leading-relaxed mb-2 line-clamp-3">
                                            {book.description}
                                        </p>
                                        <div className="flex gap-3">
                                            <button
                                                onClick={() =>
                                                    handleRate(
                                                        book.book_id,
                                                        book.title,
                                                        1,
                                                    )
                                                }
                                                className="text-xs text-gray-400 hover:text-green-500 transition-colors"
                                            >
                                                👍 Like
                                            </button>
                                            <button
                                                onClick={() =>
                                                    handleRate(
                                                        book.book_id,
                                                        book.title,
                                                        -1,
                                                    )
                                                }
                                                className="text-xs text-gray-400 hover:text-red-400 transition-colors"
                                            >
                                                👎 Dislike
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}
