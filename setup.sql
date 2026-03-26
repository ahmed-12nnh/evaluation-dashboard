-- انسخ هذا الكود بالكامل والصقه في قسم (SQL Editor) في موقع Supabase واضغط على (Run)

-- 1. إنشاء جدول المتقدمين
CREATE TABLE IF NOT EXISTS public.applicants (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    dob TEXT,
    education TEXT,
    current_task TEXT,
    address TEXT,
    google_form_url TEXT
);

-- 2. إيقاف قيود الأمان (مؤقتاً) لكي يعمل الموقع من المتصفح بدون تسجيل دخول
ALTER TABLE public.applicants DISABLE ROW LEVEL SECURITY;

-- 3. إضافة عينة بيانات وهمية لاختبار الموقع
INSERT INTO public.applicants (full_name, dob, education, current_task, address, google_form_url)
VALUES 
('أحمد محمد علي', '1990-05-12', 'بكالوريوس هندسة حاسوب', 'مهندس برمجيات', 'بغداد، الكرادة', 'https://docs.google.com/forms/d/e/1FAIpQLSd_مثال_فقط/viewform'),
('فاطمة حسن رضاء', '1995-10-22', 'ماجستير علوم سياسية', 'باحثة وأكاديمية', 'النجف الأشرف، حي الجامعة', 'https://docs.google.com/forms/d/e/1FAIpQLSd_مثال_فقط/viewform');
