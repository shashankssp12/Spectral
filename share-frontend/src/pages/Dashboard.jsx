import { useEffect, useState } from 'react'
import { getProfile } from '../actions/auth'
import { AnimatePresence, motion } from 'framer-motion'
import { FileIcon, UploadIcon, FolderIcon, LogOutIcon, Share2Icon, Trash2Icon, UserPlusIcon, GlobeIcon, LockIcon, XIcon, Share2, File } from 'lucide-react'
import { deleteFile, editFile, getFiles, uploadFile, getSimiliarFiles } from '../actions/files'


const Dashboard = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [similarFiles, setSimilarFiles] = useState([]);
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      window.location.href = '/'
    }
    (async () => {
      const profile = await getProfile();

      if (profile.error) {
        alert(profile.error);
        return;
      }
    })()


  }, []);

  useEffect(() => {
    (async () => {
      const filesData = await getFiles();

      if (filesData.error) {
        alert(filesData.error);
        return;
      }

      if (filesData) {
        setFiles(filesData)
      }
    })()
  }, [])


  const [files, setFiles] = useState([])

  const [editingFile, setEditingFile] = useState(null)

  const handlePermissionChange = async (fileId, share_type) => {
    await editFile(fileId, { share_type })
    setFiles(files?.map(file =>
      file.id === fileId ? { ...file, share_type, assignees: share_type === 'specific' ? file.assignees : [] } : file
    ))
  }

  const handleAssigneeChange = async (fileId, share_to) => {
    const file = files.find(file => file.id === fileId)
    if (file.shared_to.includes(share_to)) {
      return
    }
    await editFile(fileId, { shared_to: [...file.shared_to, share_to] })
    setFiles(files?.map(file =>
      file.id === fileId ? { ...file, shared_to: [...file.shared_to, share_to] } : file
    ))
  }

  const handleRemoveAssignee = async (fileId, share_to) => {
    await editFile(fileId, { shared_to: files.find(file => file.id === fileId).shared_to.filter(a => a !== share_to) })
    setFiles(files?.map(file =>
      file.id === fileId ? { ...file, shared_to: file.shared_to.filter(a => a !== share_to) } : file
    ))
  }

  const handleDelete = async (fileId) => {
    await deleteFile(fileId)
    setFiles(files.filter(file => file.id !== fileId))
  }

  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      handleUpload(file)
    }
  }
  const handleSearchDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      handleSearchUpload(file)
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      handleUpload(file)
    }
  }
  const handleSearchInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      console.log("Here")
      const file = e.target.files[0]
      handleSearchUpload(file)
    }
  }

  const handleUpload = async (file) => {
    try {
      setIsUploading(true)
      let fetchLink;
      const fileType = file.type.split('/')[0];
      if (fileType === 'image') {
        fetchLink = "image";
      } else if (fileType === 'video') {
        fetchLink = "video";
      } else {
        fetchLink = "raw";
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append("upload_preset", "myshare");
      formData.append("cloud_name", "devmdawne");

      const response = await fetch(`https://api.cloudinary.com/v1_1/devmdawne/${fetchLink}/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();

      const uploadedFile = await uploadFile(file, data.secure_url)
      setIsUploading(false)

      if (uploadedFile.error) {
        return
      }
      const newFile = {
        id: uploadedFile.id,
        file_name: file.name,
        file_type: file.type,
        file_size: data.bytes / 1000000 + ' MB',
        share_time: new Date().toISOString().split('T')[0],
        permission: uploadedFile.share_type,
        assignees: uploadedFile.shared_to
      }
      setFiles([...files, newFile])
    } catch (error) {
      console.log(error)
    }
  }

  const handleSearchUpload = async (file) => {
    try {
      setIsUploading(true)
      let fetchLink;
      const fileType = file.type.split('/')[0];
      if (fileType === 'image') {
        fetchLink = "image";
      } else if (fileType === 'video') {
        fetchLink = "video";
      } else {
        fetchLink = "raw";
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append("upload_preset", "myshare");
      formData.append("cloud_name", "devmdawne");

      const response = await fetch(`https://api.cloudinary.com/v1_1/devmdawne/${fetchLink}/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      const similarImages = await getSimiliarFiles(data.secure_url)
      setSimilarFiles(similarImages)
    } catch (error) {
      console.log(error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    window.location.href = '/'
  }

  const handleCopyLink = (fileId) => {
    const file = files.find(file => file.id === fileId)
    navigator.clipboard.writeText(`${window.location.origin}/shared-file/${file.id}`)
    alert('Link copied to clipboard')
  }

  return (

    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <FolderIcon className="h-8 w-8 text-indigo-600" />
                <span className="ml-2 text-2xl font-bold text-indigo-600">FileFlow</span>
              </div>
            </div>
            <div className="flex items-center">
              <button onClick={handleLogout} className="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                <LogOutIcon className="h-5 w-5 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      {
        isUploading && (
          <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="p-4 bg-white shadow-lg rounded-lg">
              <p className="text-lg font-semibold text-gray-900">Uploading...</p>
            </div>
          </div>
        )
      }
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Your Files</h1>

          <div className='flex gap-4 w-full justify-center items-center'>
            <motion.div
              className={`p-8 mt-4 border-2 border-dashed rounded-lg ${dragActive ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'
                }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              whileHover={{ scale: 1.01 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            >
              <h1 className="text-xl font-semibold text-gray-900 mb-4">Upload Files</h1>
              {
                <div className="text-center">
                  <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-1 text-sm text-gray-600">
                    Drag and drop your files here, or
                    <label
                      htmlFor="file-upload"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500 ml-1"
                    >
                      <span>select a file</span>
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        className="sr-only"
                        onChange={handleFileInput}
                      />
                    </label>
                  </p>
                  <p className="mt-1 text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                </div>
              }
            </motion.div>
            <motion.div
              className={`p-8 mt-4 border-2 border-dashed rounded-lg ${dragActive ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'
                }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleSearchDrop}
              whileHover={{ scale: 1.01 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            >
              <h1 className="text-xl font-semibold text-gray-900 mb-4">Find Similar</h1>
              {
                <div className="text-center">
                  <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-1 text-sm text-gray-600">
                    Drag and drop your files here, or
                    <label
                      htmlFor="file-search"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500 ml-1"
                    >
                      <span>select a file</span>
                      <input
                        id="file-search"
                        name="file-search"
                        type="file"
                        className="sr-only"
                        onChange={handleSearchInput}
                      />
                    </label>
                  </p>
                  <p className="mt-1 text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                </div>
              }
            </motion.div>
          </div>
          {
            similarFiles.length > 0 && (
              <div className="mt-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Similar Files</h2>
                {
                  similarFiles.map((file, idx) => (
                    <div key={idx} className="bg-white mt-2 shadow-md rounded-lg overflow-hidden">
                      <div className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <img src={file[0]} alt="Similar" className="h-8 w-8" />
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900">Similar Image
                                {
                                  file[1] > 0.5 ? <span className="text-green-500"> (Highly Similar)</span> : <span className="text-red-500"> (Not Similar)</span>
                                }
                              </h3>
                              <p className="text-sm text-gray-500">Matching Percentage: {file[1]}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                }
              </div>
            )
          }
          <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Shared Files</h2>
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="space-y-4">
                {
                  files.length === 0 && (
                    <li className="p-4 text-center text-gray-500">No files shared yet</li>
                  )
                }
                <AnimatePresence>
                  {files &&
                    files.map((file) => (
                      <motion.li
                        key={file.id}
                        layout
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="bg-white shadow-md rounded-lg overflow-hidden"
                      >
                        <div className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <FileIcon className="h-8 w-8 text-indigo-500" />
                              <div>
                                <h3 className="text-lg font-semibold text-gray-900">{file.file_name}</h3>
                                <p className="text-sm text-gray-500">{file.file_size} · Last modified: {new Date(file.share_time).toDateString()}</p>
                                <p className="text-sm text-gray-500">
                                  <span className="font-bold text-black">
                                    Ai generated description:
                                  </span>
                                  {file.file_description}</p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => { handleCopyLink(file.id) }}
                                className="p-2 text-gray-400 hover:text-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-full"
                                aria-label="Copy link"
                              >
                                <File className="h-5 w-5" />
                              </button>

                              <button
                                onClick={() => setEditingFile(editingFile === file.id ? null : file.id)}
                                className="p-2 text-gray-400 hover:text-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-full"
                                aria-label={editingFile === file.id ? "Close sharing options" : "Open sharing options"}
                              >
                                <Share2Icon className="h-5 w-5" />
                              </button>
                              <button
                                onClick={() => handleDelete(file.id)}
                                className="p-2 text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 rounded-full"
                                aria-label="Delete file"
                              >
                                <Trash2Icon className="h-5 w-5" />
                              </button>
                            </div>
                          </div>

                          <AnimatePresence>
                            {editingFile === file.id && (
                              <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="mt-4 space-y-4"
                              >
                                <div className="flex space-x-4">
                                  <button
                                    onClick={() => handlePermissionChange(file.id, 'private')}
                                    className={`flex-1 py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${file.share_type === 'private' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                      }`}
                                  >
                                    <LockIcon className="inline-block h-5 w-5 mr-2" />
                                    Private
                                  </button>
                                  <button
                                    onClick={() => handlePermissionChange(file.id, 'public')}
                                    className={`flex-1 py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${file.share_type === 'public' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                      }`}
                                  >
                                    <GlobeIcon className="inline-block h-5 w-5 mr-2" />
                                    Public
                                  </button>
                                  <button
                                    onClick={() => handlePermissionChange(file.id, 'specific')}
                                    className={`flex-1 py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${file.share_type === 'specific' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                      }`}
                                  >
                                    <UserPlusIcon className="inline-block h-5 w-5 mr-2" />
                                    Specific People
                                  </button>
                                </div>

                                {file.share_type === 'specific' && (
                                  <div>
                                    <div className="flex items-center space-x-2 mb-2">
                                      <input
                                        type="email"
                                        placeholder="Add email address"
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                        onKeyPress={(e) => {
                                          if (e.key === 'Enter') {
                                            const input = e.target
                                            handleAssigneeChange(file.id, input.value)
                                            input.value = ''
                                          }
                                        }}
                                      />
                                      <button
                                        onClick={() => {
                                          const input = document.querySelector('input[type="email"]')
                                          handleAssigneeChange(file.id, input.value)
                                          input.value = ''
                                        }}
                                        className="px-4 py-2 bg-indigo-500 text-white rounded-md hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                      >
                                        Add
                                      </button>
                                    </div>
                                    <ul className="space-y-2">
                                      {file?.shared_to?.map((assignee, idx) => (
                                        <li key={idx} className="flex items-center justify-between bg-gray-100 px-3 py-2 rounded-md">
                                          <span>{assignee}</span>
                                          <button
                                            onClick={() => handleRemoveAssignee(file.id, assignee)}
                                            className="text-red-500 hover:text-red-700 focus:outline-none"
                                            aria-label={`Remove ${assignee}`}
                                          >
                                            <XIcon className="h-5 w-5" />
                                          </button>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      </motion.li>
                    ))}
                </AnimatePresence>
              </ul>
            </div>
          </div>
        </div>
      </main >
    </div >)
}

export default Dashboard
