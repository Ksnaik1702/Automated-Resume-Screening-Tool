'use client'

import { useState } from 'react'

interface CandidateRow {
  rank: number
  candidate_name: string
  filename: string
  score: number
  score_pct: string
  status: string
  years_exp: number
  matched_skills: string
  missing_skills: string
  email: string
  phone: string
  tfidf_similarity: number
  reasons: string
}

export default function RecruiterDashboard() {
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobTitle, setJobTitle] = useState('Senior Python Developer & Data Engineer')
  const [loading, setLoading] = useState(false)
  const [rows, setRows] = useState<CandidateRow[]>([
    {
      rank: 1,
      candidate_name: 'Aarav Sharma',
      filename: 'resume_aarav_sharma.pdf',
      score: 0.823,
      score_pct: '82.3%',
      status: 'Shortlisted',
      years_exp: 4.5,
      matched_skills: 'python, sql, pandas, numpy, scikit-learn, fastapi, docker, git',
      missing_skills: 'data science, flask',
      email: 'aarav.sharma@example.com',
      phone: '+91 98765 43210',
      tfidf_similarity: 0.304,
      reasons: 'Matched 9/11 must-haves; TF-IDF sim: 0.30; 4.5 yrs exp meets 2.0 yrs req'
    },
    {
      rank: 2,
      candidate_name: 'Priya Patel',
      filename: 'resume_priya_patel.docx',
      score: 0.762,
      score_pct: '76.2%',
      status: 'Shortlisted',
      years_exp: 3.2,
      matched_skills: 'python, sql, pandas, numpy, scikit-learn, flask, git, nlp',
      missing_skills: 'fastapi, github, rest api',
      email: 'priya.patel@example.com',
      phone: '+91 91234 56789',
      tfidf_similarity: 0.308,
      reasons: 'Matched 8/11 must-haves; TF-IDF sim: 0.31; 3.2 yrs exp meets 2.0 yrs req'
    },
    {
      rank: 3,
      candidate_name: 'Rohan Verma',
      filename: 'resume_rohan_verma.pdf',
      score: 0.377,
      score_pct: '37.7%',
      status: 'Rejected',
      years_exp: 2.5,
      matched_skills: 'python, sql, fastapi, git, rest api',
      missing_skills: 'pandas, numpy, scikit-learn, data science, flask',
      email: 'rohan.verma@example.com',
      phone: '+91 98111 22334',
      tfidf_similarity: 0.119,
      reasons: 'Matched 5/11 must-haves; missing ML and data manipulation stack'
    },
    {
      rank: 4,
      candidate_name: 'Neha Gupta',
      filename: 'resume_neha_gupta.txt',
      score: 0.304,
      score_pct: '30.4%',
      status: 'Rejected',
      years_exp: 1.5,
      matched_skills: 'python, sql, pandas, git',
      missing_skills: 'scikit-learn, numpy, fastapi, rest api, flask',
      email: 'neha.gupta@example.com',
      phone: '+91 97654 32109',
      tfidf_similarity: 0.130,
      reasons: 'Junior profile (1.5 yrs); missing machine learning and API frameworks'
    },
    {
      rank: 5,
      candidate_name: 'Ananya Reddy',
      filename: 'resume_ananya_reddy.docx',
      score: 0.157,
      score_pct: '15.7%',
      status: 'Rejected',
      years_exp: 2.0,
      matched_skills: 'git, github',
      missing_skills: 'python, sql, pandas, numpy, scikit-learn, fastapi',
      email: 'ananya.reddy@example.com',
      phone: '+91 93456 78901',
      tfidf_similarity: 0.036,
      reasons: 'Frontend developer profile (React/CSS); role mismatch for Python Data Engineer'
    },
    {
      rank: 6,
      candidate_name: 'Vikas Kumar',
      filename: 'resume_vikas_kumar.pdf',
      score: 0.030,
      score_pct: '3.0%',
      status: 'Rejected',
      years_exp: 5.0,
      matched_skills: 'None',
      missing_skills: 'All must-have skills',
      email: 'vikas.kumar@example.com',
      phone: '+91 99887 76655',
      tfidf_similarity: 0.000,
      reasons: 'Sales & account management profile; 0% technical match'
    }
  ])
  const [filter, setFilter] = useState('ALL')
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateRow | null>(rows[0])

  // Call FastAPI to create a job requirement
  async function createDemoJob() {
    setLoading(true)
    try {
      const payload = {
        title: "Python Data Engineer & AI Specialist",
        jd_text: "Python, SQL, Pandas, NumPy, Scikit-learn, FastAPI, Git. 2+ years experience.",
        must_have: ["python", "sql", "pandas", "numpy", "scikit-learn", "fastapi", "git"],
        min_exp_years: 2.0,
        location: "Remote"
      }
      const res = await fetch("http://127.0.0.1:8000/job/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        const data = await res.json()
        setJobId(data.job_id)
        setJobTitle(payload.title)
        alert(`Job Created! Job ID: ${data.job_id}`)
      } else {
        setJobId("demo-job-101")
        alert("Demo Job set in simulation mode.")
      }
    } catch {
      setJobId("demo-job-101")
      alert("Using simulated demo job (Backend offline).")
    } finally {
      setLoading(false)
    }
  }

  // Trigger ranking from backend
  async function fetchRankings() {
    if (!jobId) {
      alert("Please create or select a job first!")
      return
    }
    setLoading(true)
    try {
      const res = await fetch(`http://127.0.0.1:8000/rank/${jobId}`, { method: "POST" })
      if (res.ok) {
        const data = await res.json()
        if (data.rankings && data.rankings.length > 0) {
          setRows(data.rankings)
          setSelectedCandidate(data.rankings[0])
        }
      }
    } catch {
      console.log("Using local state rankings.")
    } finally {
      setLoading(false)
    }
  }

  const filteredRows = rows.filter(r => {
    if (filter === 'SHORTLISTED') return r.status === 'Shortlisted'
    if (filter === 'REVIEW') return r.status === 'Under Review'
    if (filter === 'REJECTED') return r.status === 'Rejected'
    return true
  })

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <header className="border-b border-slate-200 pb-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <span>🎯</span> Automated Resume Screening Dashboard
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              AI/NLP Candidate Ranking, Skill Gap Verification, and Auditable Hiring Decisions
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={createDemoJob}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg text-sm shadow transition"
            >
              {jobId ? `Job Active: ${jobId}` : '+ Create Job'}
            </button>
            <button
              onClick={fetchRankings}
              disabled={loading}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg text-sm shadow transition"
            >
              🚀 Rank Candidates
            </button>
          </div>
        </div>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Candidates</p>
          <p className="text-2xl font-bold text-slate-800 mt-1">{rows.length}</p>
        </div>
        <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-200 shadow-sm">
          <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">Shortlisted (>=65%)</p>
          <p className="text-2xl font-bold text-emerald-800 mt-1">
            {rows.filter(r => r.status === 'Shortlisted').length}
          </p>
        </div>
        <div className="bg-amber-50 p-4 rounded-xl border border-amber-200 shadow-sm">
          <p className="text-xs font-semibold text-amber-700 uppercase tracking-wider">Under Review</p>
          <p className="text-2xl font-bold text-amber-800 mt-1">
            {rows.filter(r => r.status === 'Under Review').length}
          </p>
        </div>
        <div className="bg-rose-50 p-4 rounded-xl border border-rose-200 shadow-sm">
          <p className="text-xs font-semibold text-rose-700 uppercase tracking-wider">Rejected</p>
          <p className="text-2xl font-bold text-rose-800 mt-1">
            {rows.filter(r => r.status === 'Rejected').length}
          </p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Leaderboard Table */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <h2 className="font-semibold text-slate-800">Applicant Leaderboard</h2>
            {/* Filter buttons */}
            <div className="flex text-xs font-medium bg-slate-100 p-1 rounded-lg">
              {(['ALL', 'SHORTLISTED', 'REVIEW', 'REJECTED'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setFilter(tab)}
                  className={`px-3 py-1 rounded-md transition ${filter === tab ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Rank</th>
                  <th className="py-3 px-4">Candidate</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Exp</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredRows.map(cand => (
                  <tr
                    key={cand.rank}
                    onClick={() => setSelectedCandidate(cand)}
                    className={`cursor-pointer hover:bg-slate-50 transition ${selectedCandidate?.rank === cand.rank ? 'bg-blue-50/50' : ''}`}
                  >
                    <td className="py-3 px-4 font-bold text-slate-700">#{cand.rank}</td>
                    <td className="py-3 px-4">
                      <p className="font-semibold text-slate-900">{cand.candidate_name}</p>
                      <p className="text-xs text-slate-400">{cand.filename}</p>
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-800">{cand.score_pct}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                        cand.status === 'Shortlisted'
                          ? 'bg-emerald-100 text-emerald-800'
                          : cand.status === 'Under Review'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}>
                        {cand.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-600">{cand.years_exp}y</td>
                    <td className="py-3 px-4 text-right">
                      <button className="text-xs text-blue-600 font-semibold hover:underline">
                        Audit &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Column: Detailed Recruiter Audit Inspector */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
          <h2 className="font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center justify-between">
            <span>Candidate Audit</span>
            {selectedCandidate && (
              <span className="text-xs font-normal text-slate-500">Rank #{selectedCandidate.rank}</span>
            )}
          </h2>

          {selectedCandidate ? (
            <div className="space-y-4 text-sm">
              <div>
                <p className="text-xl font-bold text-slate-900">{selectedCandidate.candidate_name}</p>
                <p className="text-xs text-slate-500">{selectedCandidate.email} | {selectedCandidate.phone}</p>
              </div>

              <div className="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
                <div>
                  <p className="text-xs text-slate-500 font-medium">Match Score</p>
                  <p className="text-lg font-bold text-blue-600">{selectedCandidate.score_pct}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium">Experience</p>
                  <p className="text-lg font-bold text-slate-700">{selectedCandidate.years_exp} Years</p>
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-600 mb-1">Matched Must-Have Skills:</p>
                <div className="flex flex-wrap gap-1">
                  {selectedCandidate.matched_skills.split(', ').map((s, i) => (
                    <span key={i} className="bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded text-xs">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-600 mb-1">Missing Gaps (Unmet):</p>
                <div className="flex flex-wrap gap-1">
                  {selectedCandidate.missing_skills.split(', ').map((s, i) => (
                    <span key={i} className="bg-rose-50 text-rose-700 border border-rose-200 px-2 py-0.5 rounded text-xs">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
                <p className="font-semibold text-slate-700 mb-1">Recruiter Explanation:</p>
                <p className="text-slate-600 leading-relaxed">{selectedCandidate.reasons}</p>
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">Select a candidate from the table to view their complete audit.</p>
          )}
        </div>
      </div>
    </div>
  )
}
