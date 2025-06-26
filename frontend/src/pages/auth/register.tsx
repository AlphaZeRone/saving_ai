import { useState } from 'react'
import { authAPI } from '@/api/client'
import { useNavigate } from 'react-router-dom'

export default function  Register() {

    const Navigate = useNavigate()

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirm_password: ''
    })

    const [isLoading, setLoading] = useState(false)

    const [isError, setError] = useState({
        status_code: "",
        error_msg: ""
    })

    const [passwordError, setPasswordError] = useState("")

    const registerUser = async() => {

        if(formData.password != formData.confirm_password) {
            setError({
                status_code: "400",
                error_msg: "รหัสผ่านไม่ตรงกัน"
            })
            return
        }

        setLoading(true)
        try {
            const { confirm_password, ...registerData } = formData
            const response = await authAPI.register(registerData)
            setLoading(false)
            Navigate('/')
        } catch (error: any) {
            setLoading(false)
            setError({
                status_code: error.response?.status || "Unknown",
                error_msg: error.response?.data?.detail || "เกิดข้อผิดพลาด"
            })
        }
    }

    return (
        <form onSubmit={(e) => { e.preventDefault(); registerUser(); }}>
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

            <input 
            type="text"
            placeholder = "กรอกชื่อผู้ใช้งาน"
            value = {formData.username}
            onChange = {(e) => {
                setFormData({
                    ...formData,
                    username: e.target.value
                })
            }} 
            />

            <input 
            type="password" 
            placeholder = "กรอกรหัสผ่าน"
            value={formData.password}
            onChange = {(e) => {
                setFormData({
                    ...formData,
                    password: e.target.value
                })
            }}
            />

            <input 
            type="password" 
            placeholder = "ยืนยันรหัสผ่าน"
            value = {formData.confirm_password}
            onChange = {(e) => {
                setFormData({
                    ...formData,
                    confirm_password: e.target.value
                })
                if (e.target.value != formData.password) {
                    setPasswordError("รหัสผ่านไม่ตรงกัน")
                } else {
                    setPasswordError("")
                }
            }}
            />
            {passwordError && <div className = "text-red-500">{passwordError}</div>}

            <button 
            type = "submit"
            disabled = {isLoading}
            >
                {isLoading ? "กำลังสมัคร" : "สมัคร"}
            </button>

            {isError.error_msg && <div className = "text-red-500">{isError.error_msg}</div>}
        </form>
    )
}