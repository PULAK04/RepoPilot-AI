import { Link } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import { logout } from '../store'

export default function Nav() {
  const dispatch = useDispatch()
  return (
    <header className="nav">
      <Link to="/" className="brand"><span className="brandMark">RP</span> RepoPilot <b>AI</b></Link>
      <div className="navRight">
        <span className="pill">Multi-Agent Engineering</span>
        <button className="ghost" onClick={() => dispatch(logout())}>Sign out</button>
      </div>
    </header>
  )
}
