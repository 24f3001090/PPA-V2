<script setup>
defineProps({
    label: {
        type: String,
        required: true
    },
    value: {
        type: [Number, String],
        default: 0
    },
    variant: {
        type: String,
        default: 'primary'
    }
})
</script>

<template>
    <div class="stats-circle card p-3 border-0 shadow-sm">
        <small class="text-muted fw-semibold">{{ label }}</small>
        <h3 :class="['fw-bold m-0', `text-${variant}`]">
            {{ value ?? 0 }}
        </h3>
    </div>
</template>

<style scoped>
.stats-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.stats-circle:hover {
    background-color: aliceblue;
}
</style>