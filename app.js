// 🔴 ضع هنا رابط مشروعك والمفتاح المؤقت (Anon Key) من لوحة تحكم Supabase (Settings -> API)
const SUPABASE_URL = 'https://lwejubwsbhlxhadjkqnx.supabase.co';
const SUPABASE_ANON_KEY = 'ضع_مفتاح_ANON_KEY_هنا_(سيبدأ_بـ_eyJ...)';

// تهيئة Supabase
const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// عناصر الواجهة
const applicantsListDOM = document.getElementById('applicantsList');
const searchInput = document.getElementById('searchInput');
const welcomeScreen = document.getElementById('welcomeScreen');
const cvView = document.getElementById('cvView');

const cvName = document.getElementById('cvName');
const cvTask = document.getElementById('cvTask');
const cvDob = document.getElementById('cvDob');
const cvEducation = document.getElementById('cvEducation');
const cvAddress = document.getElementById('cvAddress');
const evalBtn = document.getElementById('evalBtn');

let applicantsData = [];

// جلب البيانات من قاعدة البيانات
async function fetchApplicants() {
    try {
        const { data, error } = await supabase.from('applicants').select('*');
        if (error) throw error;
        applicantsData = data;
        renderList(applicantsData);
    } catch (err) {
        console.error("Error loading applicants:", err.message);
        applicantsListDOM.innerHTML = `<li style="color:red; margin-top:20px;">تأكد من وضع المفتاح السري (Anon Key) بشكل صحيح في ملف app.js</li>`;
    }
}

// عرض القائمة الجانبية
function renderList(list) {
    applicantsListDOM.innerHTML = '';
    if (list.length === 0) {
        applicantsListDOM.innerHTML = '<li style="text-align:center; margin-top:20px; color:#aaa;">لا يوجد متقدمين بعد.</li>';
        return;
    }
    list.forEach(app => {
        const li = document.createElement('li');
        li.className = 'applicant-item';
        li.innerHTML = `
            <strong>${app.full_name}</strong>
            <span>${app.current_task}</span>
        `;
        li.onclick = () => showApplicant(app, li);
        applicantsListDOM.appendChild(li);
    });
}

// إظهار بيانات المتقدم وسط الشاشة
function showApplicant(app, listItem) {
    // تحديد العنصر المختار في القائمة
    document.querySelectorAll('.applicant-item').forEach(el => el.classList.remove('active'));
    listItem.classList.add('active');

    // إخفاء الترحيب وإظهار السيرة
    welcomeScreen.classList.add('hidden');
    
    // إزالة الانيميشن ثم إعادته لتشغيل الحركة
    cvView.classList.remove('hidden');
    cvView.style.animation = 'none';
    cvView.offsetHeight; /* trigger reflow */
    cvView.style.animation = null;

    // تعبئة البيانات
    cvName.textContent = app.full_name;
    cvTask.textContent = app.current_task;
    cvDob.textContent = app.dob;
    cvEducation.textContent = app.education;
    cvAddress.textContent = app.address;
    
    // تحديث رابط جوجل فورم الخاص بهذا المتقدم
    if(app.google_form_url && app.google_form_url.includes('http')) {
        evalBtn.href = app.google_form_url;
        evalBtn.style.display = 'inline-block';
    } else {
        evalBtn.style.display = 'none'; // إخفاء الزر إذا لم يوجد رابط
    }
}

// البحث
searchInput.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = applicantsData.filter(app => app.full_name.includes(term) || app.current_task.includes(term));
    renderList(filtered);
});

// ==== لوحة تحكم الأدمن (إضافة المتقدمين) ====
const adminModal = document.getElementById('adminModal');
const passwordModal = document.getElementById('passwordModal');
const adminToggleBtn = document.getElementById('adminToggleBtn');

// 1. طلب الباسوورد
adminToggleBtn.onclick = () => {
    passwordModal.classList.remove('hidden');
    document.getElementById('adminPassword').value = '';
};

// إغلاق المودال
document.querySelectorAll('.close-btn').forEach(btn => {
    btn.onclick = () => {
        adminModal.classList.add('hidden');
        passwordModal.classList.add('hidden');
    }
});

document.getElementById('cancelPassBtn').onclick = () => passwordModal.classList.add('hidden');

// 2. التحقق من الرقم السري
document.getElementById('verifyPassBtn').onclick = () => {
    const pass = document.getElementById('adminPassword').value;
    if(pass === '1234') { // يمكنك تغيير الباسوورد هنا
        passwordModal.classList.add('hidden');
        adminModal.classList.remove('hidden');
    } else {
        alert('الرقم السري خاطئ!');
    }
}

// 3. حفظ بيانات المتقدم الجديد
document.getElementById('addApplicantForm').onsubmit = async (e) => {
    e.preventDefault();
    
    const newApp = {
        full_name: document.getElementById('addName').value,
        dob: document.getElementById('addDob').value,
        education: document.getElementById('addEdu').value,
        current_task: document.getElementById('addTask').value,
        address: document.getElementById('addAddress').value,
        google_form_url: document.getElementById('addFormUrl').value
    };

    const submitBtn = e.target.querySelector('.submit-btn');
    submitBtn.textContent = 'جاري الإضافة...';
    submitBtn.disabled = true;

    const { data, error } = await supabase.from('applicants').insert([newApp]);
    
    submitBtn.textContent = '✅ إضافة المتقدم';
    submitBtn.disabled = false;

    if(error) {
        alert('حدث خطأ أثناء الإضافة: ' + error.message);
    } else {
        document.getElementById('adminFeedback').style.display = 'block';
        setTimeout(() => {
            document.getElementById('adminFeedback').style.display = 'none';
            adminModal.classList.add('hidden');
            e.target.reset(); // تصفير الحقول
            fetchApplicants(); // تحديث القائمة فوراً
        }, 2000);
    }
};

// بدء التطبيق
fetchApplicants();
