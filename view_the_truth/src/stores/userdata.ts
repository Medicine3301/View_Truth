import { defineStore } from 'pinia'
import axios from 'axios'

export const useDataStore = defineStore('dataStore', {
    state: () => ({
        data: []
    }),
    actions: {
        async fetchData() {
            try {
                const response = await axios.get('http://localhost:8000/api/data')
                this.data = response.data
            } catch (error) {
                console.error('Failed to fetch data:', error)
            }
        }
    }
})
