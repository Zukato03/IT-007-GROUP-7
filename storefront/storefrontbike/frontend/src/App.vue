<template>
  <nav class="sticky z-[100] h-14 inset-x-0 top-0 w-full border-b border-[#131314] bg-[#131314]/80 backdrop-blur-lg transition-all">
    <MaxWidthWrapper>
      <div class="flex h-14 items-center justify-between border-b border-[#131314]">
        <router-link to="/" class="flex z-40 font-semibold text-slate-100">
          SIKLO<span class="text-cyan-200">MNL</span>
        </router-link>
        <div class="h-full flex items-center space-x-4">
          <template v-if="user">
            <router-link
              to="#"
              class="button-ghost text-slate-100"
              @click.prevent="handleLogout"
            >
              Sign Out
            </router-link>
            <img
              v-if="user.profileImage || user.avatarUrl"
              :src="user.profileImage || user.avatarUrl"
              alt="Profile"
              class="h-8 w-8 rounded-full border-slate-300 border-[0.9px]"
            />
            <router-link
              to="/configure/upload"
              class="hidden sm:flex items-center gap-1 button"
            >
              Shop Now!
              <ArrowRight class="ml-1.5 h-5 w-5" />
            </router-link>
          </template>
          <template v-else>
            <router-link
              to="/login"
              class="button-ghost text-slate-100"
            >
              Login
            </router-link>
            <router-link
              to="/configure/upload"
              class="hidden sm:flex items-center gap-1 button"
            >
              Shop Now!
              <ArrowRight class="ml-1.5 h-5 w-5" />
            </router-link>
          </template>
          <button
            @click="isCartOpen = true"
            class="flex items-center p-2 text-slate-100 hover:text-slate-400"
            aria-label="Open Cart"
          >
            <ShoppingCart class="h-6 w-6" />
          </button>
        </div>
      </div>
    </MaxWidthWrapper>
    <CartComponent :isOpen="isCartOpen" @close="isCartOpen = false" />
  </nav>
  <RouterView />
</template>

<script setup>
import { ref, onMounted } from "vue";
import MaxWidthWrapper from "./components/MaxWidthWrapper.vue";
import { ArrowRight, ShoppingCart } from "lucide-vue-next"; // Adjust the import based on your setup

const user = ref(null);
const isCartOpen = ref(false);

const handleLogout = async () => {
  const response = await fetch("http://localhost:4000/logout", {
    method: "POST",
  });

  if (response.ok) {
    sessionStorage.removeItem("jwtToken"); // Remove the token from sessionStorage
    user.value = null; // Clear the user state
    window.location.href = "/"; // Refresh the page
  }
};

onMounted(async () => {
  if (typeof window !== "undefined") {
    // Retrieve the token and authProvider from sessionStorage
    const token = sessionStorage.getItem("jwtToken");
    const authProvider = sessionStorage.getItem("authProvider");

    console.log("JWT Token:", token);
    console.log("Auth Provider:", authProvider);

    if (!token || !authProvider) return;

    const endpoint =
      authProvider === "google"
        ? "http://localhost:4000/user"
        : "http://localhost:4000/github/user";

    try {
      const response = await fetch(endpoint, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        user.value = await response.json(); // Update the user state with the fetched data
        console.log("User Data", user.value);
      } else {
        console.error("Failed to fetch user data", response.statusText);
      }
    } catch (error) {
      console.error("Error fetching user data", error);
    }
  }
});
</script>
