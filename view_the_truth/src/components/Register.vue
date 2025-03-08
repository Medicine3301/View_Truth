<template>
    <a-layout class="layout">
        <a-page-header style="border: 1px solid rgb(235, 237, 240)" title="註冊" @back="goBack" />
        <a-layout-content style="padding: 0 50px">
            <div class="form-container">
                <a-form ref="formRef" :model="formState" :rules="rules" :label-col="labelCol" :wrapper-col="wrapperCol">
                    <a-form-item ref="name" label="用戶名稱" name="name">
                        <a-input v-model:value="formState.name" placeholder="請輸入3-12個字的用戶名">
                            <template #prefix>
                                <UserOutlined />
                            </template>
                        </a-input>
                    </a-form-item>

                    <a-form-item label="性別" name="sex">
                        <a-radio-group v-model:value="formState.sex">
                            <a-radio value="1">男性</a-radio>
                            <a-radio value="2">女性</a-radio>
                            <a-radio value="3">其他</a-radio>
                        </a-radio-group>
                    </a-form-item>

                    <a-form-item label="生日" required name="birthday">
                        <a-date-picker v-model:value="formState.birthday" :disabled-date="disabledDate"
                            placeholder="請選擇生日日期" style="width: 100%" />
                    </a-form-item>

                    <a-form-item has-feedback label="密碼" name="passwd">
                        <a-input-password v-model:value="formState.passwd" placeholder="請設置密碼">
                            <template #prefix>
                                <LockOutlined />
                            </template>
                        </a-input-password>
                    </a-form-item>

                    <a-form-item has-feedback label="確認密碼" name="checkPasswd">
                        <a-input-password v-model:value="formState.checkPasswd" placeholder="請再次輸入密碼">
                            <template #prefix>
                                <LockOutlined />
                            </template>
                        </a-input-password>
                    </a-form-item>

                    <a-form-item label="電子郵件" name="email">
                        <a-input v-model:value="formState.email" placeholder="請輸入電子郵件">
                            <template #prefix>
                                <MailOutlined />
                            </template>
                        </a-input>
                        <a-button @click="sendVerificationCode" style="width: 30%">
                            傳送驗證碼
                        </a-button>
                    </a-form-item>
                    <a-form-item label="驗證碼" name="check">
                        <a-input v-model:value="formState.verificationCode" placeholder="請輸入驗證碼">
                        </a-input>
                    </a-form-item>
                    <a-form-item :wrapper-col="{ span: 14, offset: 4 }">
                        <a-space>
                            <a-button type="primary" :loading="loading" @click="onSubmit">
                                註冊
                            </a-button>
                            <a-button @click="resetForm">
                                重置
                            </a-button>
                        </a-space>
                    </a-form-item>
                </a-form>
            </div>
        </a-layout-content>
        <a-layout-footer style="text-align: center">
            Ant Design ©2018 Created by Ant UED
        </a-layout-footer>
    </a-layout>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router';
import { Dayjs } from 'dayjs';
import { reactive, ref } from 'vue';
import type { UnwrapRef } from 'vue';
import type { Rule } from 'ant-design-vue/es/form';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons-vue';
import { useAuthStore } from '../stores/auth';
import axios from 'axios'; // 添加 axios 用於發送請求

interface FormState {
    name: string;
    birthday: Dayjs | undefined;
    sex: string;
    passwd: string;
    checkPasswd: string;
    email: string;
    verificationCode: string;
}


const router = useRouter();
const authStore = useAuthStore();
const formRef = ref();
const loading = ref(false);

const labelCol = { span: 5 };
const wrapperCol = { span: 13 };

const formState: UnwrapRef<FormState> = reactive({
    name: '',
    birthday: undefined,
    sex: '',
    passwd: '',
    checkPasswd: '',
    email: '',
    verificationCode:'',
});

// 禁用未來日期
const disabledDate = (current: Dayjs) => {
    return current && current.valueOf() > Date.now();
};

// 表單驗證規則
const validatePass = async (_rule: Rule, value: string) => {
    if (value === '') {
        return Promise.reject('請輸入密碼');
    }
    if (/\s/.test(value)) {
        return Promise.reject('密碼不能包含空格');
    }
    if (value.length < 8) {
        return Promise.reject('密碼長度至少為8個字符');
    }
    if (!/[A-Z]/.test(value)) {
        return Promise.reject('密碼必須包含至少一個大寫字母');
    }
    if (!/[a-z]/.test(value)) {
        return Promise.reject('密碼必須包含至少一個小寫字母');
    }
    if (!/[0-9]/.test(value)) {
        return Promise.reject('密碼必須包含至少一個數字');
    }
    if (formState.checkPasswd !== '') {
        formRef.value.validateFields(['checkPasswd']);
    }
    return Promise.resolve();
};

const validatePass2 = async (_rule: Rule, value: string) => {
    if (value === '') {
        return Promise.reject('請再次輸入密碼');
    }
    if (value !== formState.passwd) {
        return Promise.reject('兩次輸入的密碼不一致');
    }
    return Promise.resolve();
};

const validateEmail = async (_rule: Rule, value: string) => {
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (value === '') {
        return Promise.reject('請輸入電子郵件');
    }
    if (!emailPattern.test(value)) {
        return Promise.reject('電子郵件格式不正確');
    }
    return Promise.resolve();
};

const rules: Record<string, Rule[]> = {
    name: [
        { required: true, message: '請輸入用戶名稱', trigger: 'change' },
        { min: 3, max: 12, message: '長度必須為3-12個字', trigger: 'blur' },
    ],
    birthday: [
        { required: true, message: '請選擇生日日期', trigger: 'change', type: 'object' }
    ],
    sex: [
        { required: true, message: '請選擇性別', trigger: 'change' }
    ],
    passwd: [
        { required: true, validator: validatePass, trigger: 'change' }
    ],
    checkPasswd: [
        { required: true, validator: validatePass2, trigger: 'change' }
    ],
    email: [
        { required: true, validator: validateEmail, trigger: 'blur' }
    ],
};

// 新增的函數，用於發送驗證碼
const sendVerificationCode = async () => {
    try {
        const response = await axios.post('http://localhost:8000/api/send_verification_code', { email: formState.email });
        if (response.status === 200) {
            alert('驗證碼已發送');
        } else {
            alert('發送驗證碼失敗');
        }
    } catch (error) {
        alert('發送驗證碼時出錯');
    }
};

const onSubmit = async () => {
    try {
        loading.value = true;
        await formRef.value.validate();

        if (!formState.birthday) {
            return;
        }

        // 將 Dayjs 物件轉換為原生 Date 類型
        const birthdayDate = formState.birthday.toDate();

        const success = await authStore.register({
            name: formState.name,
            email: formState.email,
            password: formState.passwd,
            sex: formState.sex,
            birthday: birthdayDate,  // 直接傳遞 Date 類型
            verificationCode: formState.verificationCode,
        });

        if (success) {
            router.push('/');
        }
    } finally {
        loading.value = false;
    }
};

const resetForm = () => {
    formRef.value.resetFields();
};

const goBack = () => {
    router.push({ name: 'home' });
};
</script>

<style scoped>
.layout {
    min-height: 100vh;
}

.form-container {
    background: #fff;
    padding: 24px;
    min-height: 280px;
    margin: 16px;
    border-radius: 4px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.ant-form {
    max-width: 600px;
    margin: 0 auto;
    padding: 24px 0;
}

[data-theme='dark'] .form-container {
    background: #141414;
}
</style>