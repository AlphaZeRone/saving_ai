import { useMemo } from 'react'
import type { Transaction } from '@/types/api'

interface SavingsSummaryProps {
    transactions: Transaction[]
}

export default function SavingsSummary({ transactions }: SavingsSummaryProps) {
    const { totalIncome, totalExpense, totalSaving } = useMemo(() => {
        const income = transactions.filter(t => t.type == "income").reduce((sum, t) => sum + t.amount, 0)
        const expense = transactions.filter(t => t.type == "expense").reduce((sum, t) => sum + t.amount, 0)

        return {
            totalIncome: income,
            totalExpense: expense,
            totalSaving: income - expense
        }
    }, [transactions])
}

