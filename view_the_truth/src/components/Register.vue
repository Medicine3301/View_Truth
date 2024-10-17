<template>
    <a-layout class="layout">
        <a-page-header style="border: 1px solid rgb(235, 237, 240)" title="註冊" @back="goBack" />
        <a-layout-content style="padding: 0 50px">
            <div :style="{
                background: '#fff', padding: '24px', minHeight: '280px', margin: '16px',
            }">
                <a-form ref="formRef" :model="formState" :rules="rules" :label-col="labelCol" :wrapper-col="wrapperCol">
                    <a-form-item ref="name" label="用戶名稱" name="name">
                        <a-input v-model:value="formState.name" />
                    </a-form-item>
                    <a-form-item label="性別" name="sex">
                        <a-radio-group v-model:value="formState.sex">
                            <a-radio value="1">男性</a-radio>
                            <a-radio value="2">女性</a-radio>
                            <a-radio value="3">其他</a-radio>
                        </a-radio-group>
                    </a-form-item>
                    <a-form-item label="生日" required name="birthday">
                        <a-date-picker v-model:value="formState.birthday" type="date" placeholder="請選擇生日日期"
                            style="width: 100%" />
                    </a-form-item>
                    <a-form-item has-feedback label="密碼" name="passwd">
                        <a-input v-model:value="formState.passwd" type="password" autocomplete="off" />
                    </a-form-item>
                    <a-form-item has-feedback label="再次輸入密碼" name="checkPasswd">
                        <a-input v-model:value="formState.checkPasswd" type="password" autocomplete="off" />
                    </a-form-item>
                    <a-form-item ref="gmail" label="電子郵件" name="email">
                        <a-input v-model:value="formState.email" />
                    </a-form-item>
                    <a-form-item :wrapper-col="{ span: 14, offset: 4 }" style="text-align: center;">
                        <a-button type="primary" @click="onSubmit">註冊</a-button>
                        <a-button style="margin-left: 10px" @click="resetForm">取消</a-button>
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
//router
const router = useRouter(); // 使用 useRouter 來獲取 router 實例

const goBack = (): void => { // 定義 goBack 函數
    router.push({ name: 'home' }); // 使用 vue-router 導航回首頁
};

//表單部分
import { Dayjs } from 'dayjs';
import { reactive, ref, toRaw } from 'vue';
import type { UnwrapRef } from 'vue';
import type { Rule } from 'ant-design-vue/es/form';

interface FormState {
    name: string;
    birthday: Dayjs | undefined;
    sex: string;
    passwd: string;
    checkPasswd: string;
    email: string;
}
const formRef = ref();
const labelCol = { span: 5 };
const wrapperCol = { span: 13 };
const formState: UnwrapRef<FormState> = reactive({
    name: '',
    birthday: undefined,
    sex: '',
    passwd: '',
    checkPasswd: '',
    email: '',
});

//檢查輸入部分
const validatePass = async (_rule: Rule, value: string) => {
    if (value === '' || /\s/.test(value)) {
        return Promise.reject('密碼不可為空或含空白');
    }
    else {
        if (formState.checkPasswd !== '') {
            formRef.value.validateFields('checkPasswd');
        }
        return Promise.resolve();
    }
};
const validatePass2 = async (_rule: Rule, value: string) => {
    if (value === '') {
        return Promise.reject('請再次輸入密碼');
    } else if (value !== formState.passwd) {
        return Promise.reject("輸入的密碼不一致!");
    } else {
        return Promise.resolve();
    }
};
const validateEmail = async (_rule: Rule, value: string) => {
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (value === '') {
        return Promise.reject('請輸入電子郵件');
    } else if (!emailPattern.test(value)) {
        return Promise.reject('電子郵件格式不正確');
    } else {
        return Promise.resolve();
    }
};

const rules: Record<string, Rule[]> = {
    name: [
        { required: true, message: '請輸入用戶名稱', trigger: 'change' },
        { min: 3, max: 5, message: '長度必須3-5個字', trigger: 'blur' },
    ],
    birthday: [{ required: true, message: '請選擇生日日期', trigger: 'change', type: 'object' }],
    sex: [{ required: true, message: '請選擇您的性別', trigger: 'change' }],
    passwd: [{ required: true, validator: validatePass, trigger: 'change' }],
    checkPasswd: [{ validator: validatePass2, trigger: 'change' }],
    email: [{ required: true, validator: validateEmail, trigger: 'blur' }], // 添加電子郵件格式驗證
};
const onSubmit = () => {
    formRef.value
        .validate()
        .then(() => {
            console.log('values', formState, toRaw(formState));
        })
        .catch(error => {
            console.log('error', error);
        });
};
const resetForm = () => {
    formRef.value.resetFields();
};
</script>
<style scoped>
.site-layout-content {
    min-height: 280px;
    padding: 24px;
    background: #fff;
}

#components-layout-demo-top .logo {
    float: left;
    width: 120px;
    height: 31px;
    margin: 16px 24px 16px 0;
    background: rgba(255, 255, 255, 0.3);
}

.ant-row-rtl #components-layout-demo-top .logo {
    float: right;
    margin: 16px 0 16px 24px;
}

[data-theme='dark'] .site-layout-content {
    background: #141414;
}
</style>