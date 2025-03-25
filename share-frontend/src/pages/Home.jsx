import { motion } from 'framer-motion'
import { ChevronRightIcon, FileIcon, Share2Icon, ShieldIcon, UserIcon } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="min-h-scree flex flex-col justify-center items-center p-4 overflow-hidden">
      <div class="absolute top-0 z-[-2] h-screen w-screen bg-neutral-950 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]"></div>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center mb-12"
      >
        <motion.h1
          className="text-5xl md:text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-tr from-white to-gray-800 mb-4"
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 10 }}
        >
          FileFlow
        </motion.h1>
        <motion.p
          className="text-xl md:text-2xl text-transparent bg-clip-text bg-gradient-to-tr from-indigo-800 to-gray-400 max-w-2xl mx-auto"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.8 }}
        >
          Seamless file sharing for the modern world. Fast, secure, and effortless.
        </motion.p>
      </motion.div>

      <motion.div
        className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.8 }}
      >
        <FeatureCard
          icon={<FileIcon className="w-12 h-12 text-violet-800" />}
          title="Easy Uploads"
          description="Drag and drop your files or use our intuitive interface to upload in seconds."
        />
        <FeatureCard
          icon={<Share2Icon className="w-12 h-12 text-violet-800" />}
          title="Quick Sharing"
          description="Generate shareable links instantly and control access with ease."
        />
        <FeatureCard
          icon={<ShieldIcon className="w-12 h-12 text-violet-800" />}
          title="Secure Storage"
          description="Your files are encrypted and stored safely in our state-of-the-art servers."
        />
      </motion.div>

      <motion.div
        className="flex items-center justify-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.8 }}
      >
        <Link to="/auth" passHref>
          <motion.a
            className=" px-8 py-3 rounded-full font-semibold text-lg shadow-lg flex items-center"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <UserIcon className="w-5 h-5 mr-2" />
            <button className="inline-flex h-12 animate-shimmer items-center justify-center rounded-md border border-slate-800 bg-[linear-gradient(110deg,#000103,45%,#1e2631,55%,#000103)] bg-[length:200%_100%] px-6 font-medium text-slate-400 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-50">
              Get Started
            </button>
          </motion.a>
        </Link>
        <Link to="/dashboard" passHref>
          <motion.a
            className="px-8 py-3 rounded-full font-semibold text-lg shadow-lg"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <button className="relative inline-flex h-12 overflow-hidden rounded-full p-[1px] focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-50">
              <span className="absolute inset-[-1000%] animate-[spin_2s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#E2CBFF_0%,#393BB2_50%,#E2CBFF_100%)]" />
              <span className="inline-flex h-full w-full cursor-pointer items-center justify-center rounded-full bg-slate-950 px-6 py-1 text-sm font-medium text-white backdrop-blur-3xl">
                Go to Dashboard <ChevronRightIcon className="w-5 h-5 ml-2" />
              </span>
            </button>
          </motion.a>
        </Link>
      </motion.div>

      <motion.footer
        className="absolute bottom-4 text-center text-indigo-600"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.8 }}
      >
        <p className='text-transparent bg-clip-text bg-gradient-to-br from-violet-400 to-gray-800'>&copy; 2024 FileFlow. All rights reserved.</p>
      </motion.footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <motion.div
      className="bg-gradient-to-bl from-[#1F1E2E] to-indigo-900 p-6 rounded-xl shadow-xl"
      whileHover={{ scale: 1.05, boxShadow: '0 8px 30px rgba(0,0,0,0.12)' }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      <div className="flex flex-col items-center text-center">
        {icon}
        <h2 className="mt-4 text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-t from-gray-400 to-gray-600">{title}</h2>
        <p className="mt-2 text-transparent bg-clip-text bg-gradient-to-b from-violet-300 to-purple-800">{description}</p>
      </div>
    </motion.div>
  )
}