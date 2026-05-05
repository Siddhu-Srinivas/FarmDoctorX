import React from 'react';

const LandingPage = ({ onGetStarted }) => {
  return (
    <div className="min-h-screen bg-white font-sans text-gray-900 selection:bg-emerald-100">
      {/* Navigation Bar */}
      <nav className="fixed top-0 w-full z-50 bg-white/70 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-3xl">🌾</span>
            <span className="text-2xl font-bold bg-gradient-to-r from-emerald-700 to-green-600 bg-clip-text text-transparent italic">
              FarmDoctor
            </span>
          </div>
          
          <div className="hidden md:flex items-center gap-8 text-sm font-semibold text-gray-600">
            <a href="#features" className="hover:text-emerald-600 transition">Features</a>
            <a href="#diagnosis" className="hover:text-emerald-600 transition">Diagnosis</a>
            <a href="#weather" className="hover:text-emerald-600 transition">Weather</a>
            <button 
              onClick={onGetStarted}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-full transition shadow-lg shadow-emerald-200"
            >
              Get Started
            </button>
          </div>
          
          <button className="md:hidden text-2xl text-emerald-800">☰</button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        {/* Background Accent */}
        <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/4 w-[800px] h-[800px] bg-emerald-50 rounded-full blur-3xl opacity-60 pointer-events-none -z-10" />
        
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8 animate-in fade-in slide-in-from-left duration-1000">
            <div className="inline-flex items-center gap-2 bg-emerald-100 text-emerald-800 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Next-Gen AI Agriculture
            </div>
            
            <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight leading-tight">
              Science-Powered <span className="text-emerald-600">Growth</span> for Every Farm
            </h1>
            
            <p className="text-lg text-gray-600 leading-relaxed max-w-xl">
              From crop diagnosis to predictive yield analysis. Get expert agricultural advice in seconds with our AI-powered RAG system, trained on thousands of research papers.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <button 
                onClick={onGetStarted}
                className="px-8 py-4 bg-emerald-600 text-white rounded-xl font-bold text-lg hover:bg-emerald-700 hover:scale-105 transition active:scale-95 shadow-xl shadow-emerald-100"
              >
                Start Diagnosis
              </button>
              <button className="px-8 py-4 bg-white border-2 border-gray-100 text-gray-700 rounded-xl font-bold text-lg hover:border-emerald-200 hover:bg-emerald-50/30 transition">
                View Features
              </button>
            </div>
            
            <div className="flex items-center gap-6 pt-4">
              <div className="flex -space-x-3">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="w-10 h-10 rounded-full bg-gray-200 border-2 border-white flex items-center justify-center overflow-hidden">
                    <span className="text-lg">👨‍🌾</span>
                  </div>
                ))}
              </div>
              <p className="text-sm text-gray-500">
                Trusted by <span className="font-bold text-gray-900">5,000+</span> farmers across India
              </p>
            </div>
          </div>
          
          <div className="relative animate-in zoom-in duration-1000 delay-300">
            <div className="relative z-10 rounded-3xl overflow-hidden shadow-2xl border-4 border-white">
              <img 
                src="https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=2070" 
                alt="Modern agriculture" 
                className="w-full h-[500px] object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
            </div>
            
            {/* Floating Stats Cards */}
            <div className="absolute -bottom-6 -left-6 bg-white p-6 rounded-2xl shadow-xl z-20 border border-gray-100 animate-bounce duration-[3000ms]">
              <div className="flex items-center gap-4">
                <div className="bg-emerald-100 p-3 rounded-xl text-2xl">🌱</div>
                <div>
                  <p className="text-xs text-gray-500 font-bold uppercase">Health Score</p>
                  <p className="text-2xl font-extrabold text-emerald-600">92%</p>
                </div>
              </div>
            </div>

            <div className="absolute top-1/4 -right-10 bg-white p-6 rounded-2xl shadow-xl z-20 border border-gray-100 hidden md:block animate-pulse duration-[4000ms]">
              <div className="flex flex-col gap-1">
                <p className="text-xs text-gray-500 font-bold uppercase">Predicted Yield</p>
                <p className="text-2xl font-extrabold text-amber-600">+15.4%</p>
                <div className="w-full h-1.5 bg-gray-100 rounded-full mt-2">
                  <div className="w-3/4 h-full bg-amber-500 rounded-full" />
                </div>
              </div>
            </div>

            <div className="absolute -z-10 -top-8 -right-8 w-64 h-64 bg-amber-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob" />
            <div className="absolute -z-10 -bottom-8 -left-8 w-64 h-64 bg-emerald-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000" />
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 bg-gray-50/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-4">
            <h2 className="text-emerald-600 font-bold tracking-widest text-sm uppercase">Innovation</h2>
            <h3 className="text-4xl font-extrabold text-gray-900">Advanced AI Suite for Precision Farming</h3>
            <p className="text-gray-600">Harnessing cutting-edge technology to solve age-old agricultural challenges.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard 
              icon="🔍" 
              title="Instant Crop Diagnosis" 
              desc="Upload crop photos or describe symptoms to identify diseases and pests with 90%+ accuracy."
              color="emerald"
            />
            <FeatureCard 
              icon="🌡️" 
              title="Weather Advisory" 
              desc="Localized weather forecasting and specific farming actions based on upcoming conditions."
              color="amber"
            />
            <FeatureCard 
              icon="📈" 
              title="Yield Prediction" 
              desc="Advanced modeling based on soil, temperature, and region to estimate your harvest potential."
              color="blue"
            />
            <FeatureCard 
              icon="🌿" 
              title="Organic Solutions" 
              desc="Natural, eco-friendly pathways to manage pests and improve soil health sustainably."
              color="green"
            />
            <FeatureCard 
              icon="📋" 
              title="Farm Management" 
              desc="Keep track of your farm's history and treatments with our digital record-keeping system."
              color="purple"
            />
            <FeatureCard 
              icon="🤝" 
              title="Expert Consultation" 
              desc="Get connected with specialized recommendations based on national ICAR standards."
              color="red"
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 py-16 text-gray-400">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12">
          <div className="col-span-1 md:col-span-2 space-y-6">
            <div className="flex items-center gap-2">
              <span className="text-3xl">🌾</span>
              <span className="text-2xl font-bold text-white">FarmDoctor</span>
            </div>
            <p className="max-w-xs leading-relaxed">
              Empowering farmers with AI-driven insights to ensure food security and sustainable agricultural growth.
            </p>
            <div className="flex gap-4">
              <SocialIcon label="TW" />
              <SocialIcon label="FB" />
              <SocialIcon label="IG" />
              <SocialIcon label="LI" />
            </div>
          </div>
          
          <div className="space-y-6">
            <h4 className="text-white font-bold uppercase text-xs tracking-widest">Company</h4>
            <ul className="space-y-4 text-sm">
              <li><a href="#" className="hover:text-emerald-500 transition">About Us</a></li>
              <li><a href="#" className="hover:text-emerald-500 transition">Sustainability</a></li>
              <li><a href="#" className="hover:text-emerald-500 transition">Research</a></li>
              <li><a href="#" className="hover:text-emerald-500 transition">Careers</a></li>
            </ul>
          </div>

          <div className="space-y-6">
            <h4 className="text-white font-bold uppercase text-xs tracking-widest">Support</h4>
            <ul className="space-y-4 text-sm">
              <li><a href="#" className="hover:text-emerald-500 transition">Help Center</a></li>
              <li><a href="#" className="hover:text-emerald-500 transition">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-emerald-500 transition">Contact Expert</a></li>
              <li><a href="#" className="hover:text-emerald-500 transition">Tutorials</a></li>
            </ul>
          </div>
        </div>
        
        <div className="max-w-7xl mx-auto px-6 pt-16 mt-16 border-t border-gray-800 text-center text-xs">
          <p>© 2026 FarmDoctor AI. All rights reserved. Designed for sustainable growth.</p>
        </div>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon, title, desc, color }) => {
  const colorMap = {
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    green: 'bg-green-50 text-green-600 border-green-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
    red: 'bg-red-50 text-red-600 border-red-100',
  };

  return (
    <div className="group bg-white p-8 rounded-3xl border border-gray-100 hover:border-emerald-200 hover:shadow-2xl hover:shadow-emerald-100/40 transition-all duration-300">
      <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-2xl mb-6 shadow-sm border transition-transform group-hover:scale-110 group-hover:-rotate-6 ${colorMap[color]}`}>
        {icon}
      </div>
      <h4 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-emerald-700 transition">{title}</h4>
      <p className="text-sm text-gray-500 leading-relaxed font-medium">
        {desc}
      </p>
    </div>
  );
};

const SocialIcon = ({ label }) => (
  <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-[10px] font-bold text-white hover:bg-emerald-600 transition cursor-pointer">
    {label}
  </div>
);

export default LandingPage;
