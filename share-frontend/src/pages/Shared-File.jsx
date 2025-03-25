'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileIcon, DownloadIcon, LockIcon, LockOpenIcon, LayoutList } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { getFile } from '../actions/files'


export default function SharedFile() {
  const params = useParams()
  const fileId = params.fileId

  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')

    if (!token) {
      window.location.href = '/auth'
    }

    if (fileId) {
      getFile(fileId)
        .then((data) => {
          if (data.error) {
            setError(data.error)
          } else {
            console.log(data)
            setFile(data)
          }
        })
        .catch((error) => {
          setError(error)
        })
        .finally(() => {
          setLoading(false)
        })
    }
  }, [fileId])

  const handleDownload = () => {
    if (file) {
      window.open(file.file, '_blank')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-2xl font-semibold text-gray-600">Loading...</div>
      </div>
    )
  }

  if (error) {
    console.log(error)
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-2xl font-semibold text-red-600">{error}</div>
      </div>
    )
  }

  if (!file) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-2xl font-semibold text-gray-600">File not found</div>
      </div>
    )
  }

  if (file.share_type === 'private') {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-2xl font-semibold text-gray-600">File is private</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white shadow-lg rounded-lg overflow-hidden"
        >
          <div className="p-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-4">
                <FileIcon className="h-12 w-12 text-indigo-500" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{file.file_name}</h1>
                  <p className="text-sm text-gray-500">{file.file_size} · {file?.file_type?.toUpperCase()}</p>
                </div>
              </div>
              {file.share_type && (
                <div className="flex items-center text-yellow-600">
                  {
                    file.share_type === 'public' ?
                      <LockOpenIcon className="h-5 w-5 mr-2" /> :

                    <LockIcon className="h-5 w-5 mr-2" />
                  }
                  <span className="text-sm font-medium capitalize">
                    {file.share_type}
                  </span>
                </div>
              )}
            </div>

            <div className="mb-8">
              <div className="aspect-w-16 aspect-h-9 bg-gray-200 rounded-lg overflow-hidden">
                {file.type === 'pdf' && (
                  <embed src={file.file} type="application/pdf" width="100%" height="600px" />
                )}
                {['jpg', 'jpeg', 'png', 'gif'].includes(file.file_type) && (
                  <img src={file.file} alt={file.file_name} className="object-contain w-full h-full" />
                )}
                {!['pdf', 'jpg', 'jpeg', 'png', 'gif'].includes(file.file_type) && (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500">Preview not available</p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleDownload}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <DownloadIcon className="h-5 w-5 mr-2" />
                Download File
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}