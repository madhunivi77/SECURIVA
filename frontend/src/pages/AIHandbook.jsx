import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import { Search, BookOpen, Shield, FileText, Scale, Building2, Send, Loader2 } from "lucide-react";

const complianceStandards = [
    {
        id: "gdpr",
        name: "GDPR",
        fullName: "General Data Protection Regulation",
        category: "Privacy",
        region: "EU",
        icon: Shield,
        description: "EU regulation on data protection and privacy for all individuals within the EU and EEA.",
        color: "blue"
    },
    {
        id: "hipaa",
        name: "HIPAA",
        fullName: "Health Insurance Portability and Accountability Act",
        category: "Healthcare",
        region: "US",
        icon: FileText,
        description: "US legislation that provides data privacy and security provisions for safeguarding medical information.",
        color: "green"
    },
    {
        id: "pci_dss",
        name: "PCI-DSS",
        fullName: "Payment Card Industry Data Security Standard",
        category: "Payment",
        region: "Global",
        icon: Building2,
        description: "Information security standard for organizations that handle branded credit cards.",
        color: "purple"
    },
    {
        id: "sox",
        name: "SOX",
        fullName: "Sarbanes-Oxley Act",
        category: "Financial",
        region: "US",
        icon: Scale,
        description: "US federal law that set new or expanded requirements for all US public company boards.",
        color: "amber"
    },
    {
        id: "ccpa",
        name: "CCPA",
        fullName: "California Consumer Privacy Act",
        category: "Privacy",
        region: "US-CA",
        icon: Shield,
        description: "California state statute intended to enhance privacy rights and consumer protection.",
        color: "indigo"
    }
];

const topics = [
    "Data Collection",
    "Data Storage",
    "Data Sharing",
    "Data Deletion",
    "Breach Response",
    "User Rights",
    "Encryption",
    "Access Control",
    "Audit Logging",
    "Vendor Management"
];

function AIHandbook() {
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedCategory, setSelectedCategory] = useState("All");
    const [, setSelectedStandard] = useState(null);
    const [messages, setMessages] = useState([
        {
            role: "system",
            content: `You are a helpful AI assistant for the SECURIVA AI Handbook. You help users understand compliance standards (GDPR, HIPAA, PCI-DSS, SOX, CCPA) and cybersecurity topics.

When answering:
- Be clear, accurate, and professional
- Use the compliance tools available to provide grounded information
- Cite specific regulation articles when relevant
- Keep responses concise and easy to understand

Response style:
- Answer directly without unnecessary preamble
- Don't end with "If you have questions..." or similar phrases
- Focus on the user's specific question`
        }
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [typingMessage, setTypingMessage] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);
    const messagesContainerRef = useRef(null);
    const typingIntervalRef = useRef(null);

    // Cleanup typing interval on unmount
    useEffect(() => {
        return () => {
            if (typingIntervalRef.current) {
                clearInterval(typingIntervalRef.current);
            }
        };
    }, []);

    const scrollToBottom = () => {
        if (messagesContainerRef.current) {
            messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, typingMessage]);

    const categories = ["All", ...new Set(complianceStandards.map(s => s.category))];

    const filteredStandards = complianceStandards.filter(standard => {
        const matchesSearch = standard.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            standard.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
            standard.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCategory = selectedCategory === "All" || standard.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    const handleSendMessage = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim() || isLoading || isTyping) return;

        const userMessage = { role: "user", content: input };
        const newMessages = [...messages, userMessage];
        setMessages(newMessages);
        setInput("");
        setIsLoading(true);

        try {
            const response = await fetch("http://localhost:8000/api/chat", {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    messages: newMessages,
                    model: "gpt-4o-mini",
                    api: "openai"
                })
            });

            if (!response.ok) {
                throw new Error(`Backend error: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Start typing animation
            setIsLoading(false);
            setIsTyping(true);
            const fullText = data.response;
            let currentIndex = 0;

            // Clear any existing typing interval
            if (typingIntervalRef.current) {
                clearInterval(typingIntervalRef.current);
            }

            typingIntervalRef.current = setInterval(() => {
                if (currentIndex < fullText.length) {
                    setTypingMessage(fullText.slice(0, currentIndex + 1));
                    currentIndex++;
                } else {
                    clearInterval(typingIntervalRef.current);
                    typingIntervalRef.current = null;
                    setIsTyping(false);
                    setTypingMessage("");
                    const assistantMessage = {
                        role: "assistant",
                        content: fullText
                    };
                    setMessages([...newMessages, assistantMessage]);
                }
            }, 20); // Adjust speed by changing this value (lower = faster)

        } catch (err) {
            console.error("Chat error:", err);
            setMessages([
                ...newMessages,
                {
                    role: "assistant",
                    content: `❌ Error: ${err.message || "Failed to get response"}`
                }
            ]);
            setIsLoading(false);
            setIsTyping(false);
        }
    };

    const handleStandardClick = (standard) => {
        setSelectedStandard(standard);
        const query = `Tell me about ${standard.fullName} (${standard.name}) requirements`;
        setInput(query);
    };

    const handleTopicClick = (topic) => {
        const query = `Explain ${topic} requirements across compliance standards`;
        setInput(query);
    };

    const handleClearChat = () => {
        // Clear any ongoing typing animation
        if (typingIntervalRef.current) {
            clearInterval(typingIntervalRef.current);
            typingIntervalRef.current = null;
        }

        setMessages([
            {
                role: "system",
                content: `You are a helpful AI assistant for the SECURIVA AI Handbook. You help users understand compliance standards (GDPR, HIPAA, PCI-DSS, SOX, CCPA) and cybersecurity topics.

When answering:
- Be clear, accurate, and professional
- Use the compliance tools available to provide grounded information
- Cite specific regulation articles when relevant
- Keep responses concise and easy to understand

Response style:
- Answer directly without unnecessary preamble
- Don't end with "If you have questions..." or similar phrases
- Focus on the user's specific question`
            }
        ]);
        setInput("");
        setTypingMessage("");
        setIsTyping(false);
    };

    const colorVariants = {
        blue: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
        green: "bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20",
        purple: "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20",
        amber: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
        indigo: "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/20"
    };

    return (
        <div className="p-6 h-full overflow-auto">
            {/* Page Header */}
            <div className="mb-6">
                    <div className="flex items-center gap-3">
                        <BookOpen className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI Handbook</h1>
                            <p className="text-gray-600 dark:text-gray-400">Your compliance and security knowledge base</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Left Panel - Knowledge Base */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* Search & Filters */}
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                            <div className="space-y-4">
                                {/* Search Bar */}
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type="text"
                                        placeholder="Search compliance standards, topics, or requirements..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg 
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                             focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>

                                {/* Category Filters */}
                                <div className="flex flex-wrap gap-2">
                                    {categories.map(cat => (
                                        <button
                                            key={cat}
                                            onClick={() => setSelectedCategory(cat)}
                                            className={`px-4 py-2 rounded-lg font-medium transition-all ${selectedCategory === cat
                                                    ? "bg-blue-600 text-white"
                                                    : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                                                }`}
                                        >
                                            {cat}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Compliance Standards Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {filteredStandards.map(standard => {
                                const Icon = standard.icon;
                                return (
                                    <div
                                        key={standard.id}
                                        onClick={() => handleStandardClick(standard)}
                                        className={`p-6 rounded-lg border-2 cursor-pointer transition-all hover:shadow-lg ${colorVariants[standard.color]}`}
                                    >
                                        <div className="flex items-start gap-4">
                                            <Icon className="w-8 h-8 flex-shrink-0" />
                                            <div className="flex-1">
                                                <div className="flex items-center justify-between mb-2">
                                                    <h3 className="text-xl font-bold">{standard.name}</h3>
                                                    <span className="text-xs font-semibold px-2 py-1 rounded bg-white/50 dark:bg-black/20">
                                                        {standard.region}
                                                    </span>
                                                </div>
                                                <p className="text-sm font-medium mb-2">{standard.fullName}</p>
                                                <p className="text-sm opacity-90">{standard.description}</p>
                                                <div className="mt-3">
                                                    <span className="text-xs font-semibold px-2 py-1 rounded bg-white/50 dark:bg-black/20">
                                                        {standard.category}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Common Topics */}
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Common Topics</h2>
                            <div className="flex flex-wrap gap-2">
                                {topics.map(topic => (
                                    <button
                                        key={topic}
                                        onClick={() => handleTopicClick(topic)}
                                        className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 
                             hover:bg-blue-100 dark:hover:bg-blue-900 hover:text-blue-700 dark:hover:text-blue-300
                             transition-all font-medium text-sm"
                                    >
                                        {topic}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Right Panel - AI Chat */}
                    <div className="lg:col-span-1">
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg flex flex-col" style={{ height: 'calc(100vh - 12rem)' }}>
                            {/* Chat Header */}
                            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                            <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                            Ask AI Assistant
                                        </h2>
                                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                            Get instant answers about compliance
                                        </p>
                                    </div>
                                    <button
                                        onClick={handleClearChat}
                                        className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 
                             hover:text-blue-600 dark:hover:text-blue-400 
                             border border-gray-300 dark:border-gray-600 rounded-lg
                             hover:border-blue-500 transition-all"
                                        title="Clear conversation"
                                    >
                                        Clear
                                    </button>
                                </div>
                            </div>

                            {/* Messages */}
                            <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
                                {messages.filter(msg => msg.role !== "system").length === 0 && !isTyping ? (
                                    <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
                                        <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                        <p className="font-medium">Ask me anything about compliance!</p>
                                        <p className="text-sm mt-2">Try clicking a standard or topic to get started</p>
                                    </div>
                                ) : (
                                    <>
                                        {messages
                                            .filter(msg => msg.role !== "system")
                                            .map((msg, idx) => (
                                                <div
                                                    key={idx}
                                                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                                                >
                                                    <div
                                                        className={`max-w-[85%] rounded-lg p-3 ${msg.role === "user"
                                                                ? "bg-blue-600 text-white"
                                                                : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
                                                            }`}
                                                    >
                                                        {msg.role === "assistant" ? (
                                                            <div className="prose prose-sm dark:prose-invert max-w-none">
                                                                <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                                                                    {msg.content}
                                                                </ReactMarkdown>
                                                            </div>
                                                        ) : (
                                                            <p className="text-sm">{msg.content}</p>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        {isTyping && typingMessage && (
                                            <div className="flex justify-start">
                                                <div className="max-w-[85%] rounded-lg p-3 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white">
                                                    <div className="prose prose-sm dark:prose-invert max-w-none">
                                                        <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                                                            {typingMessage}
                                                        </ReactMarkdown>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </>
                                )}
                                {isLoading && (
                                    <div className="flex justify-start">
                                        <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-3">
                                            <Loader2 className="w-5 h-5 animate-spin text-blue-600 dark:text-blue-400" />
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input */}
                            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                                <form onSubmit={handleSendMessage} className="flex gap-2">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyPress={(e) => {
                                            if (e.key === "Enter") {
                                                e.preventDefault();
                                                handleSendMessage(e);
                                            }
                                        }}
                                        placeholder="Ask about compliance..."
                                        disabled={isLoading || isTyping}
                                        className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                             focus:ring-2 focus:ring-blue-500 focus:border-transparent
                             disabled:opacity-50"
                                    />
                                    <button
                                        type="submit"
                                        disabled={isLoading || isTyping || !input.trim()}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                             disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                                    >
                                        <Send className="w-5 h-5" />
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AIHandbook;