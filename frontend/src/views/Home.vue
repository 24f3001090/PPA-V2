<script setup>
    import { ref } from 'vue'
    import Navbar from '@/components/Navbar.vue';
    import Footer from '@/components/Footer.vue';

    const placementRecords = ref([
      { id: 1, name: 'Bipin Tiwari', company: 'Google', package: '45 LPA' },
      { id: 2, name: 'Dewashish Tikas', company: 'Google', package: '42 LPA' },
      { id: 3, name: 'Devishi Jain', company: 'TCS', package: '35 LPA' },
      { id: 4, name: 'Deepesh Gupta', company: 'Google', package: '30 LPA' },
      { id: 5, name: 'Om Pandey', company: 'Amazon', package: '30 LPA' },
      { id: 6, name: 'Yashvi Upadhyay', company: 'Google', package: '25 LPA' },
      { id: 7, name: 'Mayank Kushwaha', company: 'Amazon', package: '24 LPA' },
      { id: 8, name: 'Ilesha Shrivastava', company: 'Microsoft', package: '20 LPA' },
      { id: 9, name: 'Jeeveash Kumar', company: 'Infosys', package: '18 LPA' },
      { id: 10, name: 'Aayushmaan Patel', company: 'Google', package: '18 LPA' }
    ])
</script>

<template>
  <div class="page-container">
    <!-- Navbar -->
    <Navbar/>

    <!-- Main Section -->
    <main class="main-content">
      <!-- Left Hero Card -->
      <div class="card hero-card">
        <div class="hero-body">
          <div class="hero-text">
            <h2 class="title-dark">Begin.</h2>
            <h2 class="title-dark">Believe.</h2>
            <h2 class="title-blue">Become.</h2>
            
            <p class="tagline">
              Opportunities don't happen.<br>
              You create them.
            </p>

            <div class="quote-box">
              <span class="quote-mark">“</span>
              <div>
                <p class="quote-text">
                  I can accept failure. Everyone fails at something. But I can't accept not trying.
                </p>
                <span class="quote-author">— Michael Jordan</span>
              </div>
            </div>
          </div>

          <!-- Character Image -->
          <div class="hero-image-container">
            <img 
              src="/boy.png" 
              alt="Student Illustration" 
              class="hero-image"
            />
          </div>
        </div>

        <!-- Metrics Bar -->
        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-icon icon-blue">👥</span>
            <div>
              <div class="stat-value">300+</div>
              <div class="stat-label">Students Placed</div>
            </div>
          </div>
          
          <div class="stat-divider"></div>

          <div class="stat-item">
            <span class="stat-icon icon-green">💼</span>
            <div>
              <div class="stat-value">25+</div>
              <div class="stat-label">Top Companies</div>
            </div>
          </div>

          <div class="stat-divider"></div>

          <div class="stat-item">
            <span class="stat-icon icon-purple">📈</span>
            <div>
              <div class="stat-value">45 <small>LPA</small></div>
              <div class="stat-label">Highest Package</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Records Table Card -->
      <div class="card table-card">
        <h2 class="table-title">Last Year's Placement Records</h2>
        <div class="title-accent"></div>

        <table class="records-table">
          <thead>
            <tr>
              <th>S.No.</th>
              <th>Name</th>
              <th>Company</th>
              <th class="text-right">Package</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in placementRecords" :key="record.id">
              <td class="col-id">{{ record.id }}</td>
              <td class="col-name">{{ record.name }}</td>
              <td class="col-company">{{ record.company }}</td>
              <td class="col-package text-right">{{ record.package }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <!-- Footer -->
     <Footer/>
    </div>
</template>


<style scoped>
.main-content {
  display: flex;
  gap: 24px;
  padding: 32px 40px;
  flex: 1;
}

.card {
  background: #ffffff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

/* Left Card */
.hero-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.hero-body {
  display: flex;
  justify-content: space-between;
}

.title-dark {
  font-size: 40px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
}

.title-blue {
  font-size: 40px;
  font-weight: 800;
  color: #2563eb;
  line-height: 1.1;
  margin-bottom: 20px;
}

.tagline {
  color: #64748b;
  font-size: 16px;
  margin-bottom: 24px;
  line-height: 1.5;
}

.quote-box {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  display: flex;
  gap: 12px;
  max-width: 320px;
}

.quote-mark {
  color: #2563eb;
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
}

.quote-text {
  font-size: 13px;
  color: #475569;
  margin-bottom: 6px;
}

.quote-author {
  font-size: 12px;
  font-weight: bold;
  color: #2563eb;
}

.hero-image-container {
  display: flex;
  align-items: flex-end;
}

.hero-image {
  height: 280px;
  object-fit: contain;
}

/* Stats Footer */
.stats-bar {
  background: #ffffff;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-top: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-blue { background: #dbeafe; }
.icon-green { background: #dcfce7; }
.icon-purple { background: #f3e8ff; }

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: #e2e8f0;
}

/* Right Table Card */
.table-card {
  flex: 1;
}

.table-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}

.title-accent {
  width: 36px;
  height: 4px;
  background: #2563eb;
  border-radius: 2px;
  margin-bottom: 24px;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
}

.records-table th {
  background: #f8fafc;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  text-align: left;
  padding: 12px 16px;
}

.records-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
}

.col-id {
  color: #2563eb;
  font-weight: 700;
}

.col-name {
  font-weight: 600;
  color: #0f172a;
}

.col-company {
  color: #475569;
}

.col-package {
  font-weight: 600;
  color: #0f172a;
}

.text-right {
  text-align: right;
}
</style>