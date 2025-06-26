import { Route, Routes } from 'react-router-dom'
import Login from '@/pages/auth/login'
import Register from '@/pages/auth/register'

export default function AppRoute() {
    return (
        <Routes>
            <Route path = "/" element = {<Login />} />
            <Route path = "/login" element = {<Login />} />
            <Route path = "/signup" element = {<Register />}/>
            <Route path = "/register" element = {<Register />}/>
        </Routes>
    )
}