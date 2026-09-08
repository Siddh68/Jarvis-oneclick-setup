'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { toastAlert } from '@/components/alert-toast';
import { GOOGLE_VOICES, OPENAI_VOICES } from '@/lib/voice_constants';

export default function SetupPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        user_id: '',
        user_name: '',
        assistant_name: 'Jarvis', // Default Value
        llm_provider: 'google',
        llm_model: 'gemini-live-2.5-flash-preview-native-audio-09-2025',
        llm_voice: 'Puck',
        api_key: '',
        livekit_url: '',
        livekit_key: '',
        livekit_secret: '',
        mem0_key: '',
        google_search_key: '',
        search_engine_id: '',
        openweather_key: '',
    });

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleProviderChange = (value: string) => {
        const isGoogle = value === 'google';
        setFormData({
            ...formData,
            llm_provider: value,
            llm_model: isGoogle ? 'gemini-live-2.5-flash-preview-native-audio-09-2025' : 'gpt-4o-realtime-preview',
            llm_voice: isGoogle ? 'Puck' : 'alloy'
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const configData = {
                user_id: formData.user_id, // Use explicit input
                user_name: formData.user_name,
                assistant_name: formData.assistant_name,
                llm: {
                    provider: formData.llm_provider,
                    model: formData.llm_model,
                    voice: formData.llm_voice,
                },
                api_keys: {
                    [formData.llm_provider]: formData.api_key,
                    livekit_url: formData.livekit_url,
                    livekit_key: formData.livekit_key,
                    livekit_secret: formData.livekit_secret,
                    mem0: formData.mem0_key,
                    google_search: formData.google_search_key,
                    search_engine_id: formData.search_engine_id,
                    openweather: formData.openweather_key,
                }
            };

            const res = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configData),
            });

            if (!res.ok) throw new Error('Failed to save configuration');

            toastAlert({ title: 'SYSTEM ONLINE', description: `Initialization complete. Launching ${formData.assistant_name || 'System'}...` });

            // Artificial delay for UX
            setTimeout(() => router.push('/'), 1500);
        } catch (error) {
            toastAlert({ title: 'ERROR', description: 'Initialization failed. Check inputs.' });
        } finally {
            setLoading(false);
        }
    };

    // Helper to get available voices
    const currentVoices = formData.llm_provider === 'google' ? GOOGLE_VOICES : OPENAI_VOICES;

    return (
        <div className="min-h-screen bg-black text-white font-mono selection:bg-cyan-500/30 overflow-x-hidden relative flex items-center justify-center p-4">
            {/* Background Effects */}
            <div className="fixed inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-900 via-black to-black opacity-80 z-0 pointer-events-none" />
            <div className="fixed top-0 left-0 w-full h-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] z-0 pointer-events-none" />

            {/* Rotating HUD Rings */}
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-cyan-900/30 rounded-full animate-[spin_60s_linear_infinite] pointer-events-none z-0" />
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border border-cyan-900/20 rounded-full animate-[spin_40s_linear_infinite_reverse] pointer-events-none z-0" />

            <div className="relative z-10 w-full max-w-3xl">
                {/* Header */}
                <header className="text-center mb-12 animate-in fade-in slide-in-from-top-8 duration-700">
                    <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 tracking-tight uppercase" style={{ textShadow: '0 0 20px rgba(6,182,212,0.5)' }}>
                        {formData.assistant_name ? formData.assistant_name.split('').join('.') : 'A.I.'}
                    </h1>
                    <p className="text-cyan-600 text-xs tracking-[0.3em] mt-2">INITIAL SYSTEM CONFIGURATION</p>
                </header>

                <form onSubmit={handleSubmit} className="space-y-8 animate-in fade-in zoom-in-95 duration-700 delay-150">

                    {/* Identity & Core Module Combined for Setup */}
                    <div className="relative p-8 rounded-xl border border-cyan-500/20 bg-slate-950/80 backdrop-blur-md shadow-[0_0_30px_rgba(6,182,212,0.1)]">
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50"></div>
                        <div className="space-y-6">
                            {/* Identity Section */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <Label htmlFor="user_id" className="text-cyan-100 uppercase text-xs tracking-wider">
                                        User Name <span className="text-red-500 ml-1">*</span>
                                    </Label>
                                    <Input
                                        id="user_id"
                                        name="user_id"
                                        placeholder="unique_handle (e.g. Siddh_01)"
                                        required
                                        value={formData.user_id}
                                        onChange={(e) => {
                                            // Auto-fill display name if empty/matching
                                            const newVal = e.target.value.replace(/[^a-zA-Z0-9_-]/g, '').toLowerCase();
                                            setFormData(prev => ({
                                                ...prev,
                                                user_id: newVal,
                                                // Optional: Auto-suggest display name if currently empty
                                                // user_name: prev.user_name ? prev.user_name : e.target.value
                                            }));
                                        }}
                                        className="bg-black/50 border-cyan-900 text-cyan-300 placeholder:text-cyan-900/50 focus:border-cyan-400 font-mono py-6"
                                    />
                                    <p className="text-[10px] text-cyan-700/80 uppercase tracking-widest pl-1">
                                        ⚠️ CANNOT BE CHANGED LATER
                                    </p>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="user_name" className="text-cyan-100 uppercase text-xs tracking-wider">
                                        Full Name <span className="text-red-500 ml-1">*</span>
                                    </Label>
                                    <Input
                                        id="user_name"
                                        name="user_name"
                                        placeholder="What should I call you?"
                                        required
                                        value={formData.user_name}
                                        onChange={handleInputChange}
                                        className="bg-black/50 border-cyan-900 text-cyan-300 placeholder:text-cyan-900/50 focus:border-cyan-400 font-sans text-lg py-6"
                                    />
                                    <p className="text-[10px] text-cyan-700/80 uppercase tracking-widest pl-1">
                                        EDITABLE ANYTIME
                                    </p>
                                </div>
                            </div>

                            {/* Assistant Name Input */}
                            <div className="space-y-2">
                                <Label htmlFor="assistant_name" className="text-cyan-100 uppercase text-xs tracking-wider">
                                    Assistant Name <span className="text-red-500 ml-1">*</span>
                                </Label>
                                <Input
                                    id="assistant_name"
                                    name="assistant_name"
                                    placeholder="e.g. JARVIS"
                                    required
                                    value={formData.assistant_name}
                                    onChange={handleInputChange}
                                    className="bg-black/50 border-cyan-900 text-cyan-300 placeholder:text-cyan-900/50 focus:border-cyan-400 font-sans text-lg py-6"
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <Label className="text-cyan-100 uppercase text-xs tracking-wider">Select Model <span className="text-red-500 ml-1">*</span></Label>
                                    <Select value={formData.llm_provider} onValueChange={handleProviderChange}>
                                        <SelectTrigger className="bg-black/50 border-cyan-900 text-cyan-300">
                                            <SelectValue placeholder="Select Provider" />
                                        </SelectTrigger>
                                        <SelectContent className="bg-slate-950 border-cyan-500/50 text-cyan-300">
                                            <SelectItem value="google">GOOGLE GEMINI</SelectItem>
                                            <SelectItem value="openai">OPENAI</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <Label className="text-cyan-100 uppercase text-xs tracking-wider">Model Name <span className="text-red-500 ml-1">*</span></Label>
                                    <Select value={formData.llm_model} onValueChange={(val) => setFormData({ ...formData, llm_model: val })}>
                                        <SelectTrigger className="bg-black/50 border-cyan-900 text-cyan-300 h-auto py-2 text-left [&>span]:whitespace-normal [&>span]:break-words">
                                            <SelectValue placeholder="Select Model" />
                                        </SelectTrigger>
                                        <SelectContent className="bg-slate-950 border-cyan-500/50 text-cyan-300 max-h-[200px]">
                                            {formData.llm_provider === 'google' ? (
                                                <>
                                                    <SelectItem value="gemini-2.0-flash-exp">gemini-2.0-flash-exp</SelectItem>
                                                    <SelectItem value="gemini-2.0-flash-live-001">gemini-2.0-flash-live-001</SelectItem>
                                                    <SelectItem value="gemini-2.5-flash-native-audio-preview-09-2025">gemini-2.5-flash-native-audio-preview-09-2025</SelectItem>
                                                    <SelectItem value="gemini-2.5-flash-native-audio-preview-12-2025">gemini-2.5-flash-native-audio-preview-12-2025</SelectItem>
                                                    <SelectItem value="gemini-live-2.5-flash-native-audio">gemini-live-2.5-flash-native-audio</SelectItem>
                                                    <SelectItem value="gemini-live-2.5-flash-preview">gemini-live-2.5-flash-preview</SelectItem>
                                                    <SelectItem value="gemini-live-2.5-flash-preview-native-audio">gemini-live-2.5-flash-preview-native-audio</SelectItem>
                                                    <SelectItem value="gemini-live-2.5-flash-preview-native-audio-09-2025">gemini-live-2.5-flash-preview-native-audio-09-2025</SelectItem>
                                                </>
                                            ) : (
                                                <>
                                                    <SelectItem value="gpt-4o-realtime-preview">gpt-4o-realtime-preview</SelectItem>
                                                    <SelectItem value="gpt-realtime">gpt-realtime</SelectItem>
                                                    <SelectItem value="gpt-realtime-2025-08-28">gpt-realtime-2025-08-28</SelectItem>
                                                </>
                                            )}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="md:col-span-2 space-y-2">
                                    <Label className="text-cyan-100 uppercase text-xs tracking-wider">Select Voice <span className="text-red-500 ml-1">*</span></Label>
                                    <Select value={formData.llm_voice} onValueChange={(val) => setFormData({ ...formData, llm_voice: val })}>
                                        <SelectTrigger className="bg-black/50 border-cyan-900 text-cyan-300">
                                            <SelectValue placeholder="Select Voice" />
                                        </SelectTrigger>
                                        <SelectContent className="bg-slate-950 border-cyan-500/50 text-cyan-300 max-h-[300px]">
                                            <div className="px-2 py-1.5 text-xs font-semibold text-cyan-700/80">MALE</div>
                                            {currentVoices.male.map(v => (
                                                <SelectItem key={v} value={v}>{v}</SelectItem>
                                            ))}
                                            <div className="px-2 py-1.5 text-xs font-semibold text-cyan-700/80 mt-2">FEMALE</div>
                                            {currentVoices.female.map(v => (
                                                <SelectItem key={v} value={v}>{v}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2 md:col-span-2">
                                    <Label className="text-cyan-100 uppercase text-xs tracking-wider">Model API <span className="text-red-500 ml-1">*</span></Label>
                                    <Input
                                        id="api_key"
                                        name="api_key"
                                        type="password"
                                        required
                                        value={formData.api_key}
                                        onChange={handleInputChange}
                                        className="bg-black/50 border-cyan-900 text-cyan-300 font-mono"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Infrastructure */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* LiveKit */}
                        <div className="relative p-6 rounded-xl border border-cyan-500/20 bg-slate-950/50 backdrop-blur-md">
                            <div className="absolute top-0 right-0 p-2 text-[10px] text-cyan-800 font-bold tracking-widest opacity-50">UPLINK</div>
                            <div className="space-y-4">
                                <Label className="text-cyan-100 uppercase text-xs tracking-wider">Livekit API <span className="text-red-500 ml-1">*</span></Label>
                                <Input name="livekit_url" placeholder="URL" required value={formData.livekit_url} onChange={handleInputChange} className="bg-black/40 border-cyan-900 text-cyan-300 font-mono text-sm" />
                                <Input name="livekit_key" placeholder="API Key" type="password" required value={formData.livekit_key} onChange={handleInputChange} className="bg-black/40 border-cyan-900 text-cyan-300 font-mono text-sm" />
                                <Input name="livekit_secret" placeholder="Secret Key" type="password" required value={formData.livekit_secret} onChange={handleInputChange} className="bg-black/40 border-cyan-900 text-cyan-300 font-mono text-sm" />
                            </div>
                        </div>

                        {/* Memory */}
                        <div className="relative p-6 rounded-xl border border-purple-500/20 bg-slate-950/50 backdrop-blur-md">
                            <div className="absolute top-0 right-0 p-2 text-[10px] text-purple-800 font-bold tracking-widest opacity-50">MEMORY</div>
                            <div className="space-y-4">
                                <Label className="text-purple-100 uppercase text-xs tracking-wider">Mem0 API Key <span className="text-red-500 ml-1">*</span></Label>
                                <Input
                                    name="mem0_key"
                                    type="password"
                                    placeholder="REQUIRED"
                                    required
                                    value={formData.mem0_key}
                                    onChange={handleInputChange}
                                    className="bg-black/40 border-purple-900 text-purple-300 font-mono text-sm focus:border-purple-400"
                                />
                            </div>
                        </div>
                    </div>

                    {/* External Tools (Optional) */}
                    <div className="relative p-6 rounded-xl border border-yellow-500/20 bg-slate-950/50 backdrop-blur-md opacity-80 hover:opacity-100 transition-opacity">
                        <div className="absolute top-0 right-0 p-2 text-[10px] text-yellow-800 font-bold tracking-widest opacity-50">MODULES (OPT)</div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-2">
                                <Label className="text-yellow-100 uppercase text-[10px] tracking-wider">Google Search Key</Label>
                                <Input name="google_search_key" type="password" value={formData.google_search_key} onChange={handleInputChange} className="bg-black/40 border-yellow-900 text-yellow-300 font-mono text-xs focus:border-yellow-400 h-8" />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-yellow-100 uppercase text-[10px] tracking-wider">Engine ID</Label>
                                <Input name="search_engine_id" value={formData.search_engine_id} onChange={handleInputChange} className="bg-black/40 border-yellow-900 text-yellow-300 font-mono text-xs focus:border-yellow-400 h-8" />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-yellow-100 uppercase text-[10px] tracking-wider">OpenWeather Key <span className="text-red-500 ml-1">*</span></Label>
                                <Input name="openweather_key" type="password" required value={formData.openweather_key} onChange={handleInputChange} className="bg-black/40 border-yellow-900 text-yellow-300 font-mono text-xs focus:border-yellow-400 h-8" />
                            </div>
                        </div>
                    </div>

                    <Button
                        type="submit"
                        className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold tracking-widest uppercase py-8 text-lg shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:shadow-[0_0_40px_rgba(6,182,212,0.6)] transition-all duration-300 border border-cyan-400/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-slate-800 disabled:border-slate-700 disabled:text-slate-500 disabled:shadow-none"
                        disabled={loading || !(
                            formData.user_id &&
                            formData.user_name &&
                            formData.assistant_name &&
                            formData.api_key &&
                            formData.livekit_url &&
                            formData.livekit_key &&
                            formData.livekit_secret &&
                            formData.mem0_key &&
                            formData.openweather_key
                        )}
                    >
                        {loading ? 'INITIALIZING...' : `ACTIVATE ${formData.assistant_name ? formData.assistant_name.toUpperCase() : 'SYSTEM'} PROTOCOLS`}
                    </Button>

                </form>
            </div>

            {/* Corner Decorative Elements */}
            <div className="fixed top-0 left-0 w-32 h-32 border-l-2 border-t-2 border-cyan-500/20 rounded-tl-3xl pointer-events-none" />
            <div className="fixed top-0 right-0 w-32 h-32 border-r-2 border-t-2 border-cyan-500/20 rounded-tr-3xl pointer-events-none" />
            <div className="fixed bottom-0 left-0 w-32 h-32 border-l-2 border-b-2 border-cyan-500/20 rounded-bl-3xl pointer-events-none" />
            <div className="fixed bottom-0 right-0 w-32 h-32 border-r-2 border-b-2 border-cyan-500/20 rounded-br-3xl pointer-events-none" />
        </div>
    );
}
