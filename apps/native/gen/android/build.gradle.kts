buildscript {
    configurations.classpath { resolutionStrategy.activateDependencyLocking() }
    repositories {
        google {
            content {
                includeGroupByRegex("com[.]android.*")
                includeGroupByRegex("androidx[.].*")
                includeGroupByRegex("com[.]google[.]android.*")
                includeGroupByRegex("com[.]google[.]testing[.]platform.*")
            }
        }
        mavenCentral()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:9.3.1")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:2.2.10")
    }
}

allprojects {
    dependencyLocking {
        lockAllConfigurations()
        lockFile = rootProject.layout.projectDirectory.file("gradle/locks/${project.name}.lockfile")
    }
    repositories {
        google {
            content {
                includeGroupByRegex("com[.]android.*")
                includeGroupByRegex("androidx[.].*")
                includeGroupByRegex("com[.]google[.]android.*")
                includeGroupByRegex("com[.]google[.]testing[.]platform.*")
            }
        }
        mavenCentral()
    }
}

tasks.register("clean").configure {
    delete("build")
}

