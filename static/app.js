new Vue({
    el: '#app',
    data() {
        return {
            keywords: '',
            location: '',
            days: '1',
            jobs: [],
            filteredJobs: [],  // Initialize filteredJobs here
            scraping: false,
            search: '',
            sortKey: '',
            sortOrder: 1,
            showResults: false,
            email: '',
            emailSent: false,
            statusMessage: '',
            isLoading: false,
            darkMode: true, // Set default to true

        };
    },
    computed: {
        filteredJobs() {
            const searchTerm = this.search.toLowerCase();
            return this.jobs.filter(job =>
                Object.values(job).some(value => String(value).toLowerCase().includes(searchTerm))
            );
        }
    },

    mounted() {
        // Check for saved dark mode preference
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode !== null) {
            this.darkMode = JSON.parse(savedDarkMode);
        } else {
            // If no preference saved, set to dark mode by default
            this.darkMode = true;
            localStorage.setItem('darkMode', JSON.stringify(true));
        }
        // Apply dark mode to body
        document.body.classList.toggle('dark-mode', this.darkMode);
    },
    methods: {
        toggleDarkMode() {
            this.darkMode = !this.darkMode;
            localStorage.setItem('darkMode', JSON.stringify(this.darkMode));
            document.body.classList.toggle('dark-mode', this.darkMode);
        },
        startScraping() {
            this.scraping = true;
            this.showResults = false;
            this.emailSent = false;
            this.statusMessage = '';
            this.isLoading = true; // Show loading indicator
            this.jobs = []; // Reset jobs data to avoid previous result
            this.filteredJobs = [];
            axios.post('/scrape', {
                keywords: this.keywords,
                location: this.location,
                days: this.days
            })
            .then(response => {
                this.statusMessage = response.data.status;
                this.getResults();
            })
            .catch(error => {
                this.statusMessage = 'Error starting scraping. Please try again.';
                console.error(error);
                this.scraping = false;
                this.isLoading = false;
            });
        },
        getResults() {
            const checkInterval = setInterval(() => {
                axios.get('/scraping_status')
                    .then(response => {
                        if (response.data.status === 'Scraping finished') {
                            clearInterval(checkInterval);
                            this.scraping = false;
                            this.jobs = response.data.results;
                            this.filteredJobs = response.data.results; // Initialize with all results
                            this.showResults = true;
                            this.isLoading = false; // Hide loading indicator
                        }
                    })
                    .catch(error => {
                        console.error('Error checking status:', error);
                        clearInterval(checkInterval);
                        this.scraping = false;
                        this.isLoading = false;
                    });
            }, 2000); // Check every 2 seconds
        },
        downloadFile(filetype) {
            window.location.href = `/download/${filetype}`;
        },
        sortBy(key) {
            if (this.sortKey === key) {
                this.sortOrder *= -1;
            } else {
                this.sortKey = key;
                this.sortOrder = 1;
            }

            this.jobs.sort((a, b) => {
                let comparison = 0;
                if (a[key] > b[key]) {
                    comparison = 1;
                } else if (a[key] < b[key]) {
                    comparison = -1;
                }
                return comparison * this.sortOrder;
            });
        },
        sendEmail() {
            if (this.email) {
                axios.post('/email_results', {
                    email: this.email
                })
                .then(response => {
                    this.emailSent = true;
                    console.log(response.data);
                })
                .catch(error => {
                    console.error('Error sending email:', error);
                });
            }
        }
        
    }
});

