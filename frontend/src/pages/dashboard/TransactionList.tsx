import { useMemo } from 'react'
import type { Transaction } from '@/types/api'

interface TransactionListProps {
    transactions: Transaction[]
    onEdit ?: (transaction: Transaction) => void
    onDelete ?: (id: string) => void
    limit ?: number
    showViewAll ?: boolean
    showActions ?: boolean
}

export default function TransactionList({
    transactions,
    onEdit,
    onDelete,
    limit = 5,
    showViewAll = true,
    showActions = false
}: TransactionListProps) {
    const displayTransactions = useMemo(() => {
        return transactions.slice(0, limit)
    }, [transactions, limit])

    return (
        <div>
            <h3>รายการล่าสุด</h3>
            {displayTransactions.map(transaction => (
                <div key = {transaction.id}>
                    {transaction.description} | {transaction.amount} บาท | {transaction.type} | {transaction.category}
                </div>
            ))}
        </div>
    )
}
