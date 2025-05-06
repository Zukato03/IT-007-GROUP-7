<template>
  <div class="bg-[#1b1b1d]">
    <section
      ref="sectionRefs[0]"
      class="relative bg-cover bg-center h-screen"
      :style="{ opacity }"
    >
      <video
        autoPlay
        muted
        loop
        playsInline
        class="absolute top-0 left-0 w-full h-full object-cover"
      >
        <source src="/ad-siklo.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <MaxWidthWrapper class="pb-24 pt-10 lg:grid lg:grid-cols-3 sm:pb-32 lg:gap-x-0 xl:gap-x-8 lg:pt-24 xl:pt-32 lg:pb-52">
        <div class="col-span-2 px-6 lg:px-0 lg:pt-4">
          <div class="relative mx-auto text-center lg:text-left flex flex-col items-center lg:items-start">
            <h1 class="pl-12 relative w-fit tracking-tight mt-16 font-bold !leading-tight text-white text-5xl md:text-6xl lg:text-7xl">
              World Class Bikes
              <span class="bg-cyan-500 px-2 text-white">Specially Made</span> For You
            </h1>
          </div>
        </div>
      </MaxWidthWrapper>
    </section>

    <section class="bg-[#2b2b2e] py-16" ref="sectionRefs[1]">
      <MaxWidthWrapper class="w-full max-w-none">
        <h2 class="text-center text-4xl md:text-5xl font-bold text-slate-400">
          Explore Our Collection
        </h2>
        <div class="w-full max-w-5xl flex flex-col items-center justify-center">
          <Carousel />
        </div>
      </MaxWidthWrapper>
    </section>

    <section
      ref="sectionRefs[2]"
      class="bg-[#1b1b1d] py-24 transition-transform duration-500"
      :style="{ transform: `translateY(-${translateY}px)` }"
    >
      <MaxWidthWrapper class="flex flex-col items-center gap-16 sm:gap-32">
        <div class="flex flex-col lg:flex-row items-center gap-4 sm:gap-6">
          <h2 class="order-1 mt-2 tracking-tight text-center text-balance !leading-tight font-bold text-5xl md:text-6xl text-slate-400">
            Our
            <span class="relative px-2">
              Bestseller
              <Icons.underline class="hidden sm:block pointer-events-none absolute inset-x-0 -bottom-6 text-slate-400" />
            </span>
            Products
          </h2>
        </div>

        <div class="mx-auto grid max-w-4xl grid-cols-1 px-4 lg:mx-0 lg:max-w-none lg:grid-cols-3 gap-y-16 gap-x-8">
          <router-link
            v-for="item in items"
            :key="item.name"
            :to="item.route"
            class="transition-transform duration-300 hover:scale-110 w-50 h-50 lg:w-80 lg:h-80 cursor-pointer bg-[#131313]"
          >
            <Card>
              <CardHeader>
                <CardTitle class="text-center font-bold text-2xl text-slate-50">
                  {{ item.name }}
                </CardTitle>
              </CardHeader>
              <CardContent class="flex justify-center">
                <img :src="item.image" :alt="item.name" width="400" height="400" />
              </CardContent>
            </Card>
          </router-link>
        </div>
      </MaxWidthWrapper>
    </section>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import jwtDecode from 'jwt-decode'; // Ensure you install jwt-decode if not already
import MaxWidthWrapper from '@/components/MaxWidthWrapper';
import Carousel from '@/components/ui/carousel';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Icons from '@/components/Icons.vue';

export default {
  setup() {
    const router = useRouter();
    const route = useRoute();
    const opacity = ref(1);
    const translateY = ref(0);
    const sectionRefs = ref([]);
    const items = [
      { name: 'Bikes', route: '/bikes', image: '/bikes.png' },
      { name: 'Accessories', route: '/accessories', image: '/Garmin.png' },
      { name: 'Bike Parts', route: '/parts', image: '/DuraAce.png' },
    ];

    const handleScroll = () => {
      const scrollY = window.scrollY; // Get the current scroll position
      const newOpacity = Math.max(1 - scrollY / window.innerHeight, 0); // Calculate new opacity
      const newTranslateY = Math.min(scrollY / 2, 50); // Adjust this value to control how much it slides up
      opacity.value = newOpacity; // Update opacity state
      translateY.value = newTranslateY; // Update translation state
    };

    const checkToken = () => {
      const token = route.query.token;
      const provider = route.query.authProvider;

      if (token && provider) {
        sessionStorage.setItem('jwtToken', token);
        sessionStorage.setItem('authProvider', provider);
      }

      const storedToken = sessionStorage.getItem('jwtToken');
      if (storedToken) {
        try {
          const decoded = jwtDecode(storedToken);
          const currentTime = Date.now() / 1000; // in seconds

          if (decoded.exp && decoded.exp < currentTime) {
            sessionStorage.removeItem('jwtToken');
            router.push('/login'); // Redirect if the token is expired
          }
        } catch (error) {
          console.error('Invalid token', error);
          sessionStorage.removeItem('jwtToken');
        }
      }
    };

    const handleScrollToSection = (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const sectionIndex = sectionRefs.value.indexOf(entry.target);
          const sectionOffset =
            entry.boundingClientRect.top +
            window.scrollY -
            window.innerHeight / 2 +
            entry.target.clientHeight / 2;
          window.scrollTo({
            top: sectionOffset,
            behavior: 'smooth',
          });
        }
      });
    };

    onMounted(() => {
      window.addEventListener('scroll', handleScroll);
      checkToken();

      const observer = new IntersectionObserver(handleScrollToSection, {
        root: null,
        rootMargin: '0px',
        threshold: 0.5,
      });

      sectionRefs.value.forEach((section) => {
        if (section) {
          observer.observe(section);
        }
      });

      onBeforeUnmount(() => {
        window.removeEventListener('scroll', handleScroll);
        observer.disconnect();
      });
    });

    return {
      opacity,
      translateY,
      sectionRefs,
      items,
    };
  },
};
</script>

<style scoped>
/* Add any styles you need here */
</style>
