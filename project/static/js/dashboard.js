// Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    
    // This would normally fetch real data from the backend
    // For now we're just using the static data in the HTML
    
    // Example of how we might fetch real data:
    /*
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
        })
        .catch(error => {
            console.error('Error fetching dashboard data:', error);
        });
    */
    
    // Add hover effects to activity items
    const activityItems = document.querySelectorAll('.activity-item');
    activityItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
            this.style.transition = 'all 0.3s ease';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
});

// Example function to update dashboard data
function updateDashboardStats(data) {
    // Update summary stats
    document.querySelector('.stat-item:nth-child(1) .stat-value').textContent = data.totalTransformations;
    document.querySelector('.stat-item:nth-child(2) .stat-value').textContent = data.sugarized;
    document.querySelector('.stat-item:nth-child(3) .stat-value').textContent = data.desugarized;
    document.querySelector('.stat-item:nth-child(4) .stat-value').textContent = data.successRate + '%';
    
    // Update bar chart
    const barItems = document.querySelectorAll('.bar-item');
    data.mostCommon.forEach((item, index) => {
        if (index < barItems.length) {
            const barItem = barItems[index];
            barItem.querySelector('.bar-label').textContent = item.name;
            barItem.querySelector('.bar-fill').style.width = item.percentage + '%';
            barItem.querySelector('.bar-value').textContent = item.percentage + '%';
        }
    });
    
    // Update metrics
    document.querySelector('.metric-circle:nth-child(1) .circle-fill').setAttribute('stroke-dasharray', `${data.avgReduction}, 100`);
    document.querySelector('.metric-circle:nth-child(1) .metric-text').textContent = data.avgReduction + '%';
    
    document.querySelector('.metric-circle:nth-child(2) .circle-fill').setAttribute('stroke-dasharray', `${data.validOutput}, 100`);
    document.querySelector('.metric-circle:nth-child(2) .metric-text').textContent = data.validOutput + '%';
} 