import { useState } from 'react'
import { authAPI } from '@/api/client'
import { useNavigate } from 'react-router-dom'

export default function Login() {

    const Navigate = useNavigate()

    const [formData, setFormData] = useState({
        email: '',
        password: ''
    })

    const [isLoading, setLoading] = useState(false)

    const [isError, setError] = useState({
        status_code: "",
        error_msg: ""
    })

    const loginUser = async () => {
        setLoading(true)
        try {
            const response = await authAPI.login(formData)
            setLoading(false)
            Navigate('/dashboard')
        } catch (error: any) {
            setLoading(false)
            setError({
                status_code: error.response?.status || "Unknown",
                error_msg: error.response?.data?.detail || "เกิดข้อผิดพลาด"
            })
        }
    }

    return (
        <form onSubmit={(e) => { e.preventDefault(); loginUser();}}>
            <input 
            type="text"
            placeholder = "กรอกอีเมล"
            value = {formData.email}
            onChange = {(e) => {
                setFormData({
                    ...formData,
                    email: e.target.value
                })
            }}
            />


            <input type="password"
            placeholder = "กรอกรหัสผ่าน"
            value = {formData.password}
            onChange = {(e) => {
                setFormData({
                    ...formData,
                    password: e.target.value
                })
            }}
            />

            <button type = "submit"
            disabled = {isLoading}
            >
                {isLoading ? "กำลังเข้าสู่ระบบ" : "เข้าสู่ระบบ"}
            </button>

            {isError.error_msg && <div className = "text-red-500">{isError.error_msg}</div>}
        </form>
    )
}