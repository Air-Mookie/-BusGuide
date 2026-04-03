package com.hyeonsu.busguide.di

import com.hyeonsu.busguide.data.repository.BusGuideRepositoryImpl
import com.hyeonsu.busguide.domain.repository.BusGuideRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/** Repository DI — 인터페이스 → 구현체 바인딩 */
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds @Singleton
    abstract fun bindBusGuideRepository(impl: BusGuideRepositoryImpl): BusGuideRepository
}
